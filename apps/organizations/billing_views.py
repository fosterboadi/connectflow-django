import requests
import json
import os
import hmac
import hashlib
import logging
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.db import transaction
from django.contrib import messages
from django.urls import reverse
from .models import SubscriptionPlan, Organization, SubscriptionTransaction
from apps.accounts.models import User

logger = logging.getLogger(__name__)

@login_required
def billing_select_plan(request):
    """Allow organization admins to select/upgrade their plan."""
    user = request.user
    if not (user.is_admin or user.role == 'SUPER_ADMIN'):
        return redirect('organizations:overview')
        
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price_monthly')
    current_plan = user.organization.subscription_plan
    
    return render(request, 'organizations/billing/select_plan.html', {
        'plans': plans,
        'current_plan': current_plan,
        'organization': user.organization
    })

@login_required
def paystack_checkout(request, plan_id):
    """Initiate Paystack Transaction."""
    if not (request.user.is_admin or request.user.role == User.Role.SUPER_ADMIN):
        return HttpResponseForbidden("Only organization administrators can start checkout.")

    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
    org = request.user.organization
    
    if not plan.paystack_plan_code:
        messages.error(request, "This plan is not yet configured for Paystack payments.")
        return redirect('organizations:billing_select_plan')

    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": "Bearer " + os.environ.get("PAYSTACK_SECRET_KEY", ""),
        "Content-Type": "application/json"
    }
    payload = {
        "email": request.user.email,
        "amount": str(int(plan.price_monthly * 100)), # Paystack uses kobo/cents
        "plan": plan.paystack_plan_code,
        "callback_url": request.build_absolute_uri(reverse('organizations:billing_success')),
        "metadata": {
            "org_id": str(org.id),
            "plan_id": str(plan.id)
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        res_data = response.json()
        if res_data['status']:
            return redirect(res_data['data']['authorization_url'])
        else:
            messages.error(request, f"Paystack Error: {res_data['message']}")
    except Exception as e:
        messages.error(request, f"Connection error: {str(e)}")
        
    return redirect('organizations:billing_select_plan')

@csrf_exempt
def paystack_webhook(request):
    """
    Handle Paystack Webhooks with signature verification.
    Security: Validates Paystack signature to prevent unauthorized requests.
    """
    if request.method != 'POST':
        return HttpResponse(status=405)
    
    # Verify Paystack signature
    paystack_signature = request.headers.get('X-Paystack-Signature')
    if not paystack_signature:
        logger.warning("Paystack webhook received without signature")
        return HttpResponse(status=400)
    
    secret_key = os.environ.get('PAYSTACK_SECRET_KEY', '')
    if not secret_key:
        logger.error("PAYSTACK_SECRET_KEY not configured")
        return HttpResponse(status=500)
    
    # Compute expected signature
    computed_signature = hmac.new(
        secret_key.encode('utf-8'),
        request.body,
        hashlib.sha512
    ).hexdigest()
    
    # Verify signature matches
    if not hmac.compare_digest(paystack_signature, computed_signature):
        logger.warning("Invalid Paystack webhook signature")
        return HttpResponse(status=401)
    
    # Parse webhook data
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        logger.error("Invalid JSON in Paystack webhook")
        return HttpResponse(status=400)
    
    # Handle subscription creation event
    if data.get('event') == 'subscription.create':
        try:
            payload = data['data']
            metadata = payload['metadata']
            org = Organization.objects.get(id=metadata['org_id'])
            plan = SubscriptionPlan.objects.get(id=metadata['plan_id'], is_active=True)
            reference = payload.get('reference') or payload.get('subscription_code')

            if not reference:
                raise KeyError('reference')

            with transaction.atomic():
                transaction_record, created = SubscriptionTransaction.objects.get_or_create(
                    reference=reference,
                    defaults={
                        'organization': org,
                        'plan': plan,
                        'amount': (
                            payload.get('amount', 0) / 100
                            if payload.get('amount', 0) > 0
                            else plan.price_monthly
                        ),
                        'provider': 'paystack',
                        'status': 'success',
                    },
                )
                if created:
                    org.subscription_plan = plan
                    org.paystack_customer_id = payload['customer']['customer_code']
                    org.paystack_subscription_code = payload['subscription_code']
                    org.subscription_status = 'active'
                    org.save(update_fields=[
                        'subscription_plan',
                        'paystack_customer_id',
                        'paystack_subscription_code',
                        'subscription_status',
                    ])
            
            logger.info(f"Subscription created for org {org.id}")
            
        except (KeyError, Organization.DoesNotExist, SubscriptionPlan.DoesNotExist) as e:
            logger.error(f"Paystack webhook processing error: {e}")
            return HttpResponse(status=400)
        except Exception as e:
            logger.exception(f"Unexpected error in Paystack webhook: {e}")
            return HttpResponse(status=500)
    
    return HttpResponse(status=200)

@login_required
def billing_success(request):
    reference = request.GET.get('reference') or request.GET.get('trxref')
    if not reference or not SubscriptionTransaction.objects.filter(
        reference=reference,
        organization=request.user.organization,
        status='success',
    ).exists():
        messages.error(request, "Payment could not be verified.")
        return redirect('organizations:billing_select_plan')
    messages.success(request, "Your subscription has been updated successfully!")
    return redirect('organizations:overview')

@login_required
def select_free_plan(request, plan_id):
    """Directly assign a free plan to an organization."""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, price_monthly=0)
    org = request.user.organization
    
    if not (request.user.is_admin or request.user.role == 'SUPER_ADMIN'):
        messages.error(request, "Only organization admins can change plans.")
        return redirect('organizations:overview')

    org.subscription_plan = plan
    org.subscription_status = 'active'
    org.save()
    
    messages.success(request, f"You have successfully switched to the {plan.name} plan.")
    return redirect('organizations:overview')

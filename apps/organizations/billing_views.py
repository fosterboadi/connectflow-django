import stripe
import requests
import json
import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.urls import reverse
from .models import SubscriptionPlan, Organization

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

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
def stripe_checkout(request, plan_id):
    """Initiate Stripe Checkout session."""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    org = request.user.organization
    
    if not plan.stripe_price_id:
        messages.error(request, "This plan is not yet configured for Stripe payments.")
        return redirect('organizations:billing_select_plan')

    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=request.user.email,
            payment_method_types=['card'],
            line_items=[{'price': plan.stripe_price_id, 'quantity': 1}],
            mode='subscription',
            success_url=request.build_absolute_uri(reverse('organizations:billing_success')) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse('organizations:billing_select_plan')),
            metadata={'org_id': str(org.id), 'plan_id': str(plan.id)}
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        messages.error(request, f"Error starting Stripe checkout: {str(e)}")
        return redirect('organizations:billing_select_plan')

@login_required
def paystack_checkout(request, plan_id):
    """Initiate Paystack Transaction."""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    org = request.user.organization
    
    if not plan.paystack_plan_code:
        messages.error(request, "This plan is not yet configured for Paystack payments.")
        return redirect('organizations:billing_select_plan')

    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {os.environ.get('PAYSTACK_SECRET_KEY')}",
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
        response = requests.post(url, headers=headers, json=payload)
        res_data = response.json()
        if res_data['status']:
            return redirect(res_data['data']['authorization_url'])
        else:
            messages.error(request, f"Paystack Error: {res_data['message']}")
    except Exception as e:
        messages.error(request, f"Connection error: {str(e)}")
        
    return redirect('organizations:billing_select_plan')

@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe Webhooks."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET')
        )
    except Exception as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        org_id = session['metadata']['org_id']
        plan_id = session['metadata']['plan_id']
        
        org = Organization.objects.get(id=org_id)
        plan = SubscriptionPlan.objects.get(id=plan_id)
        
        org.subscription_plan = plan
        org.stripe_customer_id = session['customer']
        org.stripe_subscription_id = session['subscription']
        org.subscription_status = 'active'
        org.save()

    return HttpResponse(status=200)

@csrf_exempt
def paystack_webhook(request):
    """Handle Paystack Webhooks."""
    # Simplified validation: Verify with Paystack IP or signature in production
    data = json.loads(request.body)
    
    if data['event'] == 'subscription.create':
        org_id = data['data']['metadata']['org_id']
        plan_id = data['data']['metadata']['plan_id']
        
        org = Organization.objects.get(id=org_id)
        plan = SubscriptionPlan.objects.get(id=plan_id)
        
        org.subscription_plan = plan
        org.paystack_customer_id = data['data']['customer']['customer_code']
        org.paystack_subscription_code = data['data']['subscription_code']
        org.subscription_status = 'active'
        org.save()
        
    return HttpResponse(status=200)

@login_required
def billing_success(request):
    messages.success(request, "Your subscription has been updated successfully!")
    return redirect('organizations:overview')

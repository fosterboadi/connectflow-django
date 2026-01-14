from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.db.models import Count, Q, Max
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from .models import Form, FormField, FormResponse
from apps.organizations.models import Organization
import json
import csv


# ============================================
# FORM MANAGEMENT VIEWS (Managers/Creators)
# ============================================

@login_required
def form_list(request):
    """List all forms created by user or their organization"""
    user = request.user
    
    # Forms created by user
    my_forms = Form.objects.filter(created_by=user).annotate(
        total_responses=Count('responses')
    )
    
    # Organization-wide forms (if manager/admin)
    if user.organization:
        org_forms = Form.objects.filter(
            organization=user.organization
        ).exclude(created_by=user).annotate(
            total_responses=Count('responses')
        )
    else:
        org_forms = Form.objects.none()
    
    context = {
        'my_forms': my_forms,
        'org_forms': org_forms,
    }
    return render(request, 'tools/forms/form_list.html', context)


@login_required
def form_create(request):
    """Create a new form"""
    if not request.user.organization:
        messages.error(request, 'You must be part of an organization to create forms.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        form_type = request.POST.get('form_type', 'SURVEY')
        
        if not title:
            messages.error(request, 'Form title is required.')
            return render(request, 'tools/forms/form_create.html')
        
        form = Form.objects.create(
            organization=request.user.organization,
            title=title,
            description=description,
            form_type=form_type,
            created_by=request.user
        )
        
        messages.success(request, f'Form "{title}" created successfully!')
        return redirect('tools:forms:form_edit', form_id=form.id)
    
    form_types = Form.FormType.choices
    context = {
        'form_types': form_types,
    }
    return render(request, 'tools/forms/form_create.html', context)


@login_required
def form_edit(request, form_id):
    """Edit form settings and fields (Builder UI)"""
    form = get_object_or_404(Form, id=form_id)
    
    # Permission check
    if form.created_by != request.user and not request.user.is_superuser:
        messages.error(request, "You don't have permission to edit this form.")
        return redirect('tools:forms:form_list')
    
    if request.method == 'POST':
        # Update form settings
        form.title = request.POST.get('title', form.title)
        form.description = request.POST.get('description', form.description)
        form.is_public = request.POST.get('is_public') == 'on'
        form.allow_anonymous = request.POST.get('allow_anonymous') == 'on'
        form.send_email_on_submit = request.POST.get('send_email_on_submit') == 'on'
        form.notification_emails = request.POST.get('notification_emails', '')
        
        # Handle max_responses
        max_resp = request.POST.get('max_responses')
        form.max_responses = int(max_resp) if max_resp else None
        
        form.save()
        messages.success(request, 'Form settings updated!')
        return redirect('tools:forms:form_edit', form_id=form.id)
    
    context = {
        'form': form,
        'fields': form.fields.all(),
        'field_types': FormField.FieldType.choices,
        'share_url': request.build_absolute_uri(f'/f/{form.share_link}/'),
    }
    return render(request, 'tools/forms/form_edit.html', context)


@login_required
@require_http_methods(["POST"])
def form_field_add(request, form_id):
    """Add a field to the form (AJAX)"""
    form = get_object_or_404(Form, id=form_id)
    
    # Permission check
    if form.created_by != request.user and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    # Get current max order
    max_order = form.fields.aggregate(Max('order'))['order__max'] or 0
    
    field = FormField.objects.create(
        form=form,
        label=data.get('label', 'Untitled Question'),
        field_type=data.get('field_type', 'SHORT_TEXT'),
        is_required=data.get('is_required', False),
        options=data.get('options', []),
        order=max_order + 1
    )
    
    return JsonResponse({
        'success': True,
        'id': str(field.id),
        'label': field.label,
        'field_type': field.field_type,
        'order': field.order
    })


@login_required
@require_http_methods(["POST"])
def form_field_update(request, form_id, field_id):
    """Update a field (AJAX)"""
    form = get_object_or_404(Form, id=form_id)
    field = get_object_or_404(FormField, id=field_id, form=form)
    
    # Permission check
    if form.created_by != request.user and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    # Update field
    field.label = data.get('label', field.label)
    field.field_type = data.get('field_type', field.field_type)
    field.is_required = data.get('is_required', field.is_required)
    field.placeholder = data.get('placeholder', field.placeholder)
    field.help_text = data.get('help_text', field.help_text)
    field.options = data.get('options', field.options)
    field.save()
    
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def form_field_delete(request, form_id, field_id):
    """Delete a field (AJAX)"""
    form = get_object_or_404(Form, id=form_id)
    field = get_object_or_404(FormField, id=field_id, form=form)
    
    # Permission check
    if form.created_by != request.user and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    field.delete()
    return JsonResponse({'success': True})


@login_required
def form_responses(request, form_id):
    """View all responses to a form"""
    form = get_object_or_404(Form, id=form_id)
    
    # Permission check
    if form.created_by != request.user and not request.user.is_superuser:
        messages.error(request, "You don't have permission to view responses.")
        return redirect('tools:forms:form_list')
    
    responses = form.responses.all().select_related('user').order_by('-submitted_at')
    
    context = {
        'form': form,
        'responses': responses,
        'total_responses': responses.count(),
        'fields': form.fields.all(),
    }
    return render(request, 'tools/forms/form_responses.html', context)


@login_required
def form_analytics(request, form_id):
    """Show analytics and charts for form responses"""
    form = get_object_or_404(Form, id=form_id)
    
    # Permission check
    if form.created_by != request.user and not request.user.is_superuser:
        messages.error(request, "You don't have permission to view analytics.")
        return redirect('tools:forms:form_list')
    
    responses = form.responses.all()
    
    # Aggregate data for each field
    field_stats = []
    for field in form.fields.all():
        if field.field_type == FormField.FieldType.SECTION:
            continue
        
        # Extract all answers for this field
        answers = []
        for response in responses:
            answer = response.answers.get(str(field.id))
            if answer:
                answers.append(answer)
        
        # Calculate statistics based on field type
        stats = {
            'field': field,
            'total_responses': len(answers),
        }
        
        if field.field_type in ['MULTIPLE_CHOICE', 'DROPDOWN']:
            # Count each option
            from collections import Counter
            counts = Counter(answers)
            stats['options'] = [
                {'label': k, 'count': v, 'percentage': (v/len(answers)*100) if answers else 0}
                for k, v in counts.items()
            ]
        
        elif field.field_type == 'RATING':
            # Average rating
            try:
                ratings = [int(r) for r in answers if r]
                stats['average'] = sum(ratings) / len(ratings) if ratings else 0
                from collections import Counter
                stats['distribution'] = dict(Counter(ratings))
            except (ValueError, TypeError):
                stats['average'] = 0
                stats['distribution'] = {}
        
        elif field.field_type == 'NUMBER':
            # Min, max, average
            try:
                numbers = [float(n) for n in answers if n]
                stats['min'] = min(numbers) if numbers else 0
                stats['max'] = max(numbers) if numbers else 0
                stats['average'] = sum(numbers) / len(numbers) if numbers else 0
            except (ValueError, TypeError):
                stats['min'] = stats['max'] = stats['average'] = 0
        
        field_stats.append(stats)
    
    context = {
        'form': form,
        'total_responses': responses.count(),
        'field_stats': field_stats,
    }
    return render(request, 'tools/forms/form_analytics.html', context)


@login_required
def form_export_csv(request, form_id):
    """Export form responses to CSV"""
    form = get_object_or_404(Form, id=form_id)
    
    # Permission check
    if form.created_by != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("You don't have permission to export this data.")
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="form_{form.id}_responses.csv"'
    
    writer = csv.writer(response)
    
    # Header row
    fields = form.fields.all().order_by('order')
    header = ['Submitted At', 'Respondent']
    header.extend([field.label for field in fields])
    writer.writerow(header)
    
    # Data rows
    for resp in form.responses.all().order_by('-submitted_at'):
        row = [
            resp.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
            resp.respondent_name
        ]
        for field in fields:
            answer = resp.answers.get(str(field.id), '')
            row.append(answer)
        writer.writerow(row)
    
    return response


@login_required
@require_http_methods(["POST"])
def form_delete(request, form_id):
    """Delete a form"""
    form = get_object_or_404(Form, id=form_id)
    
    # Permission check
    if form.created_by != request.user and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    form_title = form.title
    form.delete()
    
    messages.success(request, f'Form "{form_title}" deleted successfully.')
    return redirect('tools:forms:form_list')


# ============================================
# PUBLIC FORM SUBMISSION VIEWS
# ============================================

def form_submit_page(request, share_link):
    """Public page for submitting a form"""
    form = get_object_or_404(Form, share_link=share_link)
    
    # Check if form is accepting responses
    if not form.is_accepting_responses:
        return render(request, 'tools/forms/form_closed.html', {'form': form})
    
    # Check login requirement
    if form.require_login and not request.user.is_authenticated:
        messages.warning(request, 'Please login to submit this form.')
        return redirect('accounts:login')
    
    if request.method == 'POST':
        # Collect answers
        answers = {}
        errors = []
        
        for field in form.fields.all():
            if field.field_type == FormField.FieldType.SECTION:
                continue
            
            field_name = f'field_{field.id}'
            answer = request.POST.get(field_name)
            
            # Validation
            if field.is_required and not answer:
                errors.append(f'{field.label} is required.')
                continue
            
            if answer:
                answers[str(field.id)] = answer
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('form_submit', share_link=share_link)
        
        # Create response
        response = FormResponse.objects.create(
            form=form,
            user=request.user if request.user.is_authenticated else None,
            is_anonymous=form.allow_anonymous,
            answers=answers,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # TODO: Send notification email if enabled
        # if form.send_email_on_submit and form.notification_emails:
        #     send_form_notification_email(form, response)
        
        messages.success(request, 'Your response has been submitted!')
        return redirect('form_submit_success', share_link=share_link)
    
    context = {
        'form': form,
        'fields': form.fields.all().order_by('order'),
    }
    return render(request, 'tools/forms/form_submit.html', context)


def form_submit_success(request, share_link):
    """Thank you page after submission"""
    form = get_object_or_404(Form, share_link=share_link)
    return render(request, 'tools/forms/form_success.html', {'form': form})

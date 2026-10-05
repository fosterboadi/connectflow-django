from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import LeaveType, LeaveRequest, LeaveBalance
from .forms import LeaveRequestForm, LeaveTypeForm
from decimal import Decimal


def _organization_leave_request_form(request):
    form = LeaveRequestForm(request.POST or None)
    form.fields['leave_type'].queryset = LeaveType.objects.filter(
        organization=request.user.organization
    )
    return form

@login_required
def leave_list(request):
    """View user's leave requests and balances"""
    org = request.user.organization
    my_requests = LeaveRequest.objects.filter(user=request.user).order_by('-start_date')
    my_balances = LeaveBalance.objects.filter(user=request.user, year=timezone.now().year)
    
    # Manager/Admin view for pending requests
    pending_approvals = None
    if request.user.is_admin or request.user.role in ['SUPER_ADMIN', 'TEAM_MANAGER']:
        # If admin, see all. If manager, see team? (Simplifying to all org for now)
        pending_approvals = LeaveRequest.objects.filter(
            leave_type__organization=org,
            status=LeaveRequest.Status.PENDING
        ).exclude(user=request.user)
    
    context = {
        'my_requests': my_requests,
        'my_balances': my_balances,
        'pending_approvals': pending_approvals,
        'is_admin': request.user.is_admin or request.user.role == 'SUPER_ADMIN',
    }
    return render(request, 'tools/timeoff/index.html', context)

@login_required
def leave_request_create(request):
    """Submit a new leave request"""
    form = _organization_leave_request_form(request)
    if request.method == 'POST' and form.is_valid():
        leave_request = form.save(commit=False)
        leave_request.user = request.user
        leave_request.total_days = Decimal(
            (leave_request.end_date - leave_request.start_date).days + 1
        )
        if leave_request.leave_type.counts_as_leave:
            balance = LeaveBalance.objects.filter(
                user=request.user,
                leave_type=leave_request.leave_type,
                year=leave_request.start_date.year,
            ).first()
            if balance and balance.remaining < leave_request.total_days:
                messages.error(request, f"Insufficient balance. You have {balance.remaining} days remaining.")
                return render(request, 'tools/timeoff/request_form.html', {'form': form, 'title': 'Request Time Off'})
        leave_request.save()
        messages.success(request, "Leave request submitted.")
        return redirect('tools:timeoff:index')

    return render(request, 'tools/timeoff/request_form.html', {'form': form, 'title': 'Request Time Off'})


@login_required
def leave_request_edit(request, pk):
    """Edit a user's pending leave request."""
    leave_request = get_object_or_404(LeaveRequest, pk=pk, user=request.user)
    if leave_request.status != LeaveRequest.Status.PENDING:
        messages.error(request, "Only pending leave requests can be edited.")
        return redirect('tools:timeoff:index')

    form = _organization_leave_request_form(request)
    if request.method == 'GET':
        form.initial = {
            'leave_type': leave_request.leave_type,
            'start_date': leave_request.start_date,
            'end_date': leave_request.end_date,
            'reason': leave_request.reason,
        }
    elif form.is_valid():
        leave_request.leave_type = form.cleaned_data['leave_type']
        leave_request.start_date = form.cleaned_data['start_date']
        leave_request.end_date = form.cleaned_data['end_date']
        leave_request.reason = form.cleaned_data['reason']
        leave_request.total_days = Decimal(
            (leave_request.end_date - leave_request.start_date).days + 1
        )
        if leave_request.leave_type.counts_as_leave:
            balance = LeaveBalance.objects.filter(
                user=request.user,
                leave_type=leave_request.leave_type,
                year=leave_request.start_date.year,
            ).first()
            if balance and balance.remaining < leave_request.total_days:
                messages.error(request, f"Insufficient balance. You have {balance.remaining} days remaining.")
                return render(request, 'tools/timeoff/request_form.html', {
                    'form': form,
                    'title': 'Edit Time Off Request',
                    'leave_request': leave_request,
                })
        leave_request.save()
        messages.success(request, "Leave request updated.")
        return redirect('tools:timeoff:index')

    return render(request, 'tools/timeoff/request_form.html', {
        'form': form,
        'title': 'Edit Time Off Request',
        'leave_request': leave_request,
    })


@login_required
def leave_request_cancel(request, pk):
    """Withdraw a user's pending leave request."""
    leave_request = get_object_or_404(LeaveRequest, pk=pk, user=request.user)
    if request.method == 'POST' and leave_request.status == LeaveRequest.Status.PENDING:
        leave_request.status = LeaveRequest.Status.CANCELLED
        leave_request.save(update_fields=['status', 'updated_at'])
        messages.success(request, "Leave request withdrawn.")
    return redirect('tools:timeoff:index')

@login_required
def leave_approve(request, pk, action):
    """Approve or reject a leave request"""
    if not (request.user.is_admin or request.user.role in ['SUPER_ADMIN', 'TEAM_MANAGER']):
        messages.error(request, "Permission denied.")
        return redirect('tools:timeoff:index')
        
    leave_request = get_object_or_404(LeaveRequest, pk=pk, leave_type__organization=request.user.organization)
    
    if action == 'approve' and leave_request.status == LeaveRequest.Status.PENDING:
        leave_request.status = LeaveRequest.Status.APPROVED
        leave_request.approved_by = request.user
        
        # Deduct from balance
        if leave_request.leave_type.counts_as_leave:
            balance, _ = LeaveBalance.objects.get_or_create(
                user=leave_request.user,
                leave_type=leave_request.leave_type,
                year=leave_request.start_date.year
            )
            balance.used += leave_request.total_days
            balance.save()
            
        messages.success(request, f"Leave for {leave_request.user.get_full_name()} approved.")
    elif action == 'reject' and leave_request.status == LeaveRequest.Status.PENDING:
        leave_request.status = LeaveRequest.Status.REJECTED
        leave_request.approved_by = request.user
        messages.warning(request, f"Leave for {leave_request.user.get_full_name()} rejected.")
        
    elif leave_request.status != LeaveRequest.Status.PENDING:
        messages.info(request, "This leave request has already been processed.")
        return redirect('tools:timeoff:index')

    leave_request.save()
    return redirect('tools:timeoff:index')
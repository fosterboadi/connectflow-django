from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Resource, Booking
from .forms import ResourceForm, BookingForm

@login_required
def booking_list(request):
    """View bookable resources and user's bookings"""
    org = request.user.organization
    resources = Resource.objects.filter(organization=org, is_active=True)
    my_bookings = Booking.objects.filter(user=request.user).order_by('-start_time')
    
    # Check for approval permissions
    pending_approvals = None
    if request.user.is_admin or request.user.role == 'SUPER_ADMIN':
        pending_approvals = Booking.objects.filter(
            resource__organization=org,
            status=Booking.Status.PENDING
        )
    
    context = {
        'resources': resources,
        'my_bookings': my_bookings,
        'pending_approvals': pending_approvals,
        'is_admin': request.user.is_admin or request.user.role == 'SUPER_ADMIN',
    }
    return render(request, 'tools/bookings/index.html', context)

@login_required
def resource_create(request):
    """Create a new bookable resource (Admin only)"""
    if not (request.user.is_admin or request.user.role == 'SUPER_ADMIN'):
        messages.error(request, "Permission denied.")
        return redirect('tools:bookings:index')
        
    if request.method == 'POST':
        form = ResourceForm(request.POST)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.organization = request.user.organization
            resource.save()
            messages.success(request, "Resource created successfully.")
            return redirect('tools:bookings:index')
    else:
        form = ResourceForm()
        
    return render(request, 'tools/bookings/resource_form.html', {'form': form, 'title': 'Add Resource'})


@login_required
def resource_edit(request, pk):
    """Edit a bookable resource (Admin only)."""
    if not (request.user.is_admin or request.user.role == 'SUPER_ADMIN'):
        messages.error(request, "Permission denied.")
        return redirect('tools:bookings:index')

    resource = get_object_or_404(Resource, pk=pk, organization=request.user.organization)
    form = ResourceForm(request.POST or None, instance=resource)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Resource updated successfully.")
        return redirect('tools:bookings:index')

    return render(request, 'tools/bookings/resource_form.html', {
        'form': form,
        'title': 'Edit Resource',
        'resource': resource,
    })


@login_required
def resource_delete(request, pk):
    """Deactivate a bookable resource (Admin only)."""
    if not (request.user.is_admin or request.user.role == 'SUPER_ADMIN'):
        messages.error(request, "Permission denied.")
        return redirect('tools:bookings:index')

    resource = get_object_or_404(Resource, pk=pk, organization=request.user.organization)
    if request.method == 'POST':
        resource.is_active = False
        resource.save(update_fields=['is_active', 'updated_at'])
        messages.success(request, "Resource removed from the booking list.")
    return redirect('tools:bookings:index')

@login_required
def booking_create(request, resource_id):
    """Create a new booking for a specific resource"""
    resource = get_object_or_404(Resource, id=resource_id, organization=request.user.organization)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.resource = resource
            booking.user = request.user
            
            # Auto-confirm if approval not required
            if not resource.requires_approval:
                booking.status = Booking.Status.CONFIRMED
            else:
                booking.status = Booking.Status.PENDING
                
            booking.save()
            
            msg = "Booking submitted and awaiting approval." if resource.requires_approval else "Booking confirmed!"
            messages.success(request, msg)
            return redirect('tools:bookings:index')
    else:
        form = BookingForm()
        
    return render(request, 'tools/bookings/booking_form.html', {
        'form': form, 
        'resource': resource,
        'title': f'Book {resource.name}'
    })


@login_required
def booking_edit(request, pk):
    """Edit a user's pending booking."""
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if booking.status != Booking.Status.PENDING:
        messages.error(request, "Only pending bookings can be edited.")
        return redirect('tools:bookings:index')

    form = BookingForm(request.POST or None, instance=booking)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Booking updated successfully.")
        return redirect('tools:bookings:index')

    return render(request, 'tools/bookings/booking_form.html', {
        'form': form,
        'resource': booking.resource,
        'title': f'Edit {booking.resource.name} booking',
        'booking': booking,
    })

@login_required
def booking_cancel(request, pk):
    """Cancel a booking"""
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if request.method == 'POST' and booking.status in [Booking.Status.PENDING, Booking.Status.CONFIRMED]:
        booking.status = Booking.Status.CANCELLED
        booking.save()
        messages.success(request, "Booking cancelled.")
    return redirect('tools:bookings:index')

@login_required
@require_POST
def booking_approve(request, pk, action):
    """Approve or reject a booking (Admin only)"""
    if not (request.user.is_admin or request.user.role == 'SUPER_ADMIN'):
        messages.error(request, "Permission denied.")
        return redirect('tools:bookings:index')
        
    booking = get_object_or_404(Booking, pk=pk, resource__organization=request.user.organization)
    
    if action == 'approve':
        booking.status = Booking.Status.CONFIRMED
        booking.approved_by = request.user
        messages.success(request, f"Booking for {booking.user.get_full_name()} approved.")
    elif action == 'reject':
        booking.status = Booking.Status.CANCELLED
        messages.warning(request, f"Booking for {booking.user.get_full_name()} rejected.")
        
    booking.save()
    return redirect('tools:bookings:index')
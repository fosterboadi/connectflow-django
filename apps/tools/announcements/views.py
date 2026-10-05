from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import models
from .models import Announcement, AnnouncementReadReceipt
from .forms import AnnouncementForm
from apps.organizations.models import Department, Team


def _organization_announcement_form(request, instance=None):
    form = AnnouncementForm(request.POST or None, instance=instance)
    organization = request.user.organization
    form.fields['target_department'].queryset = Department.objects.filter(
        organization=organization,
        is_active=True,
    )
    form.fields['target_team'].queryset = Team.objects.filter(
        department__organization=organization,
        is_active=True,
    )
    return form

@login_required
def announcement_list(request):
    """View active announcements for the user"""
    org = request.user.organization
    now = timezone.now()
    
    # Filter announcements by organization, publication status, and scheduling
    announcements = Announcement.objects.filter(
        organization=org,
        is_published=True
    ).filter(
        models.Q(scheduled_at__isnull=True) | models.Q(scheduled_at__lte=now)
    ).filter(
        models.Q(expires_at__isnull=True) | models.Q(expires_at__gte=now)
    ).order_by('-is_pinned', '-created_at')
    
    context = {
        'announcements': announcements,
        'is_admin': request.user.is_admin or request.user.role == 'SUPER_ADMIN',
    }
    return render(request, 'tools/announcements/index.html', context)

@login_required
def announcement_create(request):
    """Create a new announcement (Admin only)"""
    if not (request.user.is_admin or request.user.role == 'SUPER_ADMIN'):
        messages.error(request, "You don't have permission to create announcements.")
        return redirect('tools:announcements:index')
        
    if request.method == 'POST':
        form = _organization_announcement_form(request)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.organization = request.user.organization
            announcement.created_by = request.user
            announcement.save()
            messages.success(request, "Announcement created successfully.")
            return redirect('tools:announcements:index')
    else:
        form = _organization_announcement_form(request)
        
    return render(request, 'tools/announcements/form.html', {
        'form': form,
        'title': 'Create Announcement'
    })

@login_required
def announcement_edit(request, pk):
    """Edit an existing announcement (Admin only)"""
    announcement = get_object_or_404(Announcement, pk=pk, organization=request.user.organization)
    
    if not (request.user.is_admin or request.user.role == 'SUPER_ADMIN'):
        messages.error(request, "You don't have permission to edit announcements.")
        return redirect('tools:announcements:index')
        
    if request.method == 'POST':
        form = _organization_announcement_form(request, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, "Announcement updated successfully.")
            return redirect('tools:announcements:index')
    else:
        form = _organization_announcement_form(request, instance=announcement)
        
    return render(request, 'tools/announcements/form.html', {
        'form': form,
        'title': 'Edit Announcement',
        'announcement': announcement
    })

@login_required
def announcement_delete(request, pk):
    """Delete an announcement (Admin only)"""
    announcement = get_object_or_404(Announcement, pk=pk, organization=request.user.organization)
    
    if request.method != 'POST':
        messages.error(request, "Use the delete action to remove this announcement.")
    elif not (request.user.is_admin or request.user.role == 'SUPER_ADMIN'):
        messages.error(request, "You don't have permission to delete announcements.")
    else:
        announcement.delete()
        messages.success(request, "Announcement deleted successfully.")
        
    return redirect('tools:announcements:index')

@login_required
def acknowledge_announcement(request, pk):
    """Acknowledge reading an announcement"""
    announcement = get_object_or_404(Announcement, pk=pk, organization=request.user.organization)
    
    receipt, created = AnnouncementReadReceipt.objects.get_or_create(
        announcement=announcement,
        user=request.user
    )
    
    if not receipt.acknowledged_at:
        receipt.acknowledged_at = timezone.now()
        receipt.save()
        messages.success(request, f"Acknowledged: {announcement.title}")
        
    return redirect('tools:announcements:index')

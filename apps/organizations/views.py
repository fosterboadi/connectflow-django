from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.http import Http404
from .models import (
    Organization, Department, Team, SharedProject, ProjectFile, ProjectMeeting, 
    ProjectTask, ProjectMilestone, ProjectRiskRegister, AuditTrail, ControlTest, 
    ComplianceRequirement, ComplianceEvidence
)
from .forms import (
    DepartmentForm, TeamForm, InviteMemberForm, SharedProjectForm, JoinProjectForm,
    ProjectFileForm, ProjectMeetingForm, ProjectTaskForm, ProjectMilestoneForm, OrganizationForm,
    ProjectRiskForm, AuditTrailForm, ControlTestForm, ComplianceEvidenceForm, ComplianceRequirementForm
)


def get_user_project_or_404(user, pk):
    """
    Secure helper to get project with organization validation.
    Returns project only if user's organization is host or guest.
    Raises Http404 if not found or no access.
    """
    try:
        project = SharedProject.objects.get(pk=pk)
        
        # Check if user's org is host or guest
        is_host = project.host_organization == user.organization
        is_guest = user.organization in project.guest_organizations.all()
        
        if not (is_host or is_guest):
            raise Http404("Project not found")
        
        return project
    except SharedProject.DoesNotExist:
        raise Http404("Project not found")


@login_required
def project_risk_dashboard(request, pk):
    """
    Unified Risk & Compliance Dashboard for PMs, Auditors, and Compliance Officers.
    """
    project = get_user_project_or_404(request.user, pk)

    # Gatekeeper: Check Governance Suite Access
    if not project.host_organization.has_feature('has_governance_suite'):
        messages.warning(request, f"The Governance Suite (Risk & Compliance) is a premium feature. Please upgrade the host organization's ({project.host_organization.name}) plan to gain access.")
        return redirect('organizations:shared_project_detail', pk=pk)

    risks = project.risks.all()
    audits = project.audits.all()
    compliance_reqs = project.compliance_requirements.all()
    
    # Calculate Compliance metrics
    applicable_reqs = compliance_reqs.filter(applicable=True).count()
    covered_reqs = compliance_reqs.filter(evidence__review_status='APPROVED').distinct().count()
    compliance_gap = 100 - (int((covered_reqs / applicable_reqs) * 100) if applicable_reqs > 0 else 0)
    
    # Control Effectiveness
    tests = project.control_tests.all()
    control_effectiveness = 0
    if tests.exists():
        passed = tests.filter(test_result='PASS').count()
        control_effectiveness = int((passed / tests.count()) * 100)

    context = {
        'project': project,
        'risks': risks,
        'audits': audits,
        'compliance_reqs': compliance_reqs,
        'risk_form': ProjectRiskForm(project=project),
        'audit_form': AuditTrailForm(),
        'control_form': ControlTestForm(),
        'compliance_form': ComplianceRequirementForm(project=project),
        'evidence_form': ComplianceEvidenceForm(),
        'metrics': {
            'financial_risks': risks.filter(category='FIN').order_by('-impact'),
            'compliance_risks': risks.filter(category='COM').order_by('-impact'),
            'open_audit_findings': sum(len(audit.findings) if isinstance(audit.findings, list) else 0 for audit in audits),
            'compliance_gap_percentage': compliance_gap,
            'control_effectiveness': control_effectiveness,
        }
    }
    return render(request, 'organizations/risk_dashboard.html', context)


@login_required
@require_POST
def add_compliance_requirement(request, pk):
    project = get_user_project_or_404(request.user, pk)
    if not (request.user.is_admin or request.user.role == 'COMPLIANCE_OFFICER'):
        return JsonResponse({'success': False}, status=403)
    
    form = ComplianceRequirementForm(request.POST, project=project)
    if form.is_valid():
        req = form.save(commit=False)
        req.project = project
        req.save()
        messages.success(request, 'Regulatory requirement added.')
    return redirect('organizations:project_risk_dashboard', pk=pk)


@login_required
@require_POST
def delete_compliance_requirement(request, pk, req_pk):
    project = get_user_project_or_404(request.user, pk)
    req = get_object_or_404(ComplianceRequirement, pk=req_pk, project=project)
    if request.user.is_admin or request.user.role == 'COMPLIANCE_OFFICER':
        req.delete()
        messages.success(request, 'Requirement removed.')
    return redirect('organizations:project_risk_dashboard', pk=pk)


@login_required
@require_POST
def delete_compliance_evidence(request, pk, evidence_pk):
    project = get_user_project_or_404(request.user, pk)
    evidence = get_object_or_404(ComplianceEvidence, pk=evidence_pk, requirement__project=project)
    if request.user.is_admin or request.user == evidence.uploaded_by:
        evidence.delete()
        messages.success(request, 'Evidence removed.')
    return redirect('organizations:project_risk_dashboard', pk=pk)


@login_required
@require_POST
def add_project_risk(request, pk):
    project = get_user_project_or_404(request.user, pk)
    
    form = ProjectRiskForm(request.POST, project=project)
    if form.is_valid():
        risk = form.save(commit=False)
        risk.project = project
        risk.save()
        messages.success(request, 'Risk added to the register.')
        return redirect('organizations:project_risk_dashboard', pk=pk)
    messages.error(request, 'Failed to add risk. Please check the form.')
    return redirect('organizations:project_risk_dashboard', pk=pk)


@login_required
@require_POST
def add_audit_trail(request, pk):
    project = get_user_project_or_404(request.user, pk)
    
    form = AuditTrailForm(request.POST)
    if form.is_valid():
        audit = form.save(commit=False)
        audit.project = project
        audit.auditor = request.user
        
        # Handle findings as a list if it's text
        findings_raw = form.cleaned_data['findings']
        if isinstance(findings_raw, str):
            import json
            try:
                # Try to parse as JSON list
                audit.findings = json.loads(findings_raw)
                if not isinstance(audit.findings, list):
                    audit.findings = [findings_raw]
            except json.JSONDecodeError:
                # If not JSON, split by lines or just wrap in list
                audit.findings = [f.strip() for f in findings_raw.split('\n') if f.strip()]
        
        audit.save()
        messages.success(request, 'Audit trail recorded.')
        return redirect('organizations:project_risk_dashboard', pk=pk)
    return redirect('organizations:project_risk_dashboard', pk=pk)


@login_required
@require_POST
def add_control_test(request, pk):
    project = get_user_project_or_404(request.user, pk)
    
    form = ControlTestForm(request.POST)
    if form.is_valid():
        test = form.save(commit=False)
        test.project = project
        test.tester = request.user
        test.save()
        messages.success(request, 'Control test results saved.')
        return redirect('organizations:project_risk_dashboard', pk=pk)
    return redirect('organizations:project_risk_dashboard', pk=pk)


@login_required
@require_POST
def add_compliance_evidence(request, pk, req_pk):
    project = get_user_project_or_404(request.user, pk)
    requirement = get_object_or_404(ComplianceRequirement, pk=req_pk, project=project)
    
    # Already validated via get_user_project_or_404
    
    # Check Storage Limit
    org = project.host_organization
    current_usage_mb = org.get_storage_usage()
    max_storage_mb = org.get_plan().max_storage_mb
    
    uploaded_file = request.FILES.get('document')
    if uploaded_file:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if (current_usage_mb + file_size_mb) > max_storage_mb:
            messages.error(request, f"Upload failed: File would exceed storage limit. You have {round(max_storage_mb - current_usage_mb, 2)} MB remaining.")
            return redirect('organizations:project_risk_dashboard', pk=pk)

    form = ComplianceEvidenceForm(request.POST, request.FILES)
    if form.is_valid():
        evidence = form.save(commit=False)
        evidence.requirement = requirement
        evidence.uploaded_by = request.user
        evidence.save()
        messages.success(request, 'Compliance evidence uploaded.')
        return redirect('organizations:project_risk_dashboard', pk=pk)
    return redirect('organizations:project_risk_dashboard', pk=pk)


@login_required
def organization_settings(request):
    """Allow admins to edit organization details, like logo and name."""
    user = request.user
    if not user.is_admin or not user.organization:
        messages.error(request, "Only organization admins can access settings.")
        return redirect('organizations:overview')
    
    organization = user.organization
    
    if request.method == 'POST':
        form = OrganizationForm(request.POST, request.FILES, instance=organization)
        if form.is_valid():
            # Gatekeeper: Check Custom Branding for Logo Upload
            if 'logo' in request.FILES and not organization.has_feature('has_custom_branding'):
                messages.error(request, f"Custom branding (logo upload) is a premium feature. Please upgrade your plan ({organization.get_plan().name}) to access it.")
                return render(request, 'organizations/organization_form.html', {
                    'form': form,
                    'organization': organization,
                    'action': 'Update Settings'
                })

            form.save()
            messages.success(request, "Organization details updated successfully!")
            return redirect('organizations:organization_settings')
    else:
        form = OrganizationForm(instance=organization)
    
    return render(request, 'organizations/organization_form.html', {
        'form': form,
        'organization': organization,
        'action': 'Update Settings'
    })


@login_required
def project_milestones(request, pk):
    project = get_user_project_or_404(request.user, pk)
    
    if request.method == 'POST':
        form = ProjectMilestoneForm(request.POST)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.project = project
            milestone.save()
            
            # Notify members
            from apps.accounts.models import Notification
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            channel_layer = get_channel_layer()
            
            for member in project.members.all():
                if member == request.user: continue
                notification = Notification.notify(
                    recipient=member,
                    sender=request.user,
                    title=f"New Milestone: {milestone.title}",
                    content=f"A new milestone has been set for {project.name}: {milestone.title}",
                    notification_type='PROJECT',
                    link=reverse('organizations:shared_project_detail', kwargs={'pk': project.pk})
                )
                async_to_sync(channel_layer.group_send)(
                    f"notifications_{member.id}",
                    {
                        'type': 'send_notification',
                        'id': str(notification.id),
                        'title': notification.title,
                        'content': notification.content,
                        'notification_type': notification.notification_type,
                        'link': notification.link,
                    }
                )
            
            messages.success(request, 'Milestone added.')
            return redirect('organizations:project_milestones', pk=pk)
    else:
        form = ProjectMilestoneForm()
        
    return render(request, 'organizations/project_milestones.html', {
        'project': project,
        'milestones': project.milestones.all(),
        'form': form
    })


@login_required
@require_POST
def toggle_milestone(request, pk):
    milestone = get_object_or_404(ProjectMilestone, pk=pk)
    if request.user not in milestone.project.members.all():
        return JsonResponse({'success': False}, status=403)
        
    from django.utils import timezone
    milestone.is_completed = not milestone.is_completed
    milestone.completed_at = timezone.now() if milestone.is_completed else None
    milestone.save()

    from apps.accounts.models import Notification
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer
    channel_layer = get_channel_layer()
    
    title = f"Milestone Achieved: {milestone.title}" if milestone.is_completed else f"Milestone Re-opened: {milestone.title}"
    status_text = "completed" if milestone.is_completed else "re-opened"
    
    for member in milestone.project.members.all():
        if member == request.user:
            continue
            
        notification = Notification.notify(
            recipient=member,
            sender=request.user,
            title=title,
            content=f"{request.user.get_full_name()} {status_text} a milestone in {milestone.project.name}.",
            notification_type='PROJECT',
            link=reverse('organizations:shared_project_detail', kwargs={'pk': milestone.project.pk})
        )
        
        async_to_sync(channel_layer.group_send)(
            f"notifications_{member.id}",
            {
                'type': 'send_notification',
                'id': str(notification.id),
                'title': notification.title,
                'content': notification.content,
                'notification_type': notification.notification_type,
                'link': notification.link,
            }
        )
    
    return JsonResponse({
        'success': True, 
        'is_completed': milestone.is_completed,
        'completed_at': milestone.completed_at.strftime('%Y-%m-%d %H:%M') if milestone.completed_at else None
    })


@login_required
def project_files(request, pk):
    project = get_user_project_or_404(request.user, pk)
    
    if request.method == 'POST':
        # Check Organization Storage Limit
        org = project.host_organization
        current_usage_mb = org.get_storage_usage()
        max_storage_mb = org.get_plan().max_storage_mb
        
        # Get incoming file size
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            file_size_mb = uploaded_file.size / (1024 * 1024)
            if (current_usage_mb + file_size_mb) > max_storage_mb:
                messages.error(request, f"Upload failed: This file ({round(file_size_mb, 2)} MB) would exceed your remaining storage space. You have {round(max_storage_mb - current_usage_mb, 2)} MB left.")
                return redirect('organizations:project_files', pk=pk)

        form = ProjectFileForm(request.POST, request.FILES)
        if form.is_valid():
            project_file = form.save(commit=False)
            project_file.project = project
            project_file.uploader = request.user
            # For CloudinaryField, form validation handles the upload
            project_file.save()

            # Notification logic
            from apps.accounts.models import Notification
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            channel_layer = get_channel_layer()
            
            for member in project.members.all():
                if member == request.user:
                    continue
                notification = Notification.notify(
                    recipient=member,
                    sender=request.user,
                    title=f"New File in {project.name}",
                    content=f"{request.user.get_full_name()} uploaded {project_file.name}",
                    notification_type='PROJECT',
                    link=reverse('organizations:project_files', kwargs={'pk': project.pk})
                )
                async_to_sync(channel_layer.group_send)(
                    f"notifications_{member.id}",
                    {
                        'type': 'send_notification',
                        'id': str(notification.id),
                        'title': notification.title,
                        'content': notification.content,
                        'notification_type': notification.notification_type,
                        'link': notification.link,
                    }
                )

            messages.success(request, 'File uploaded successfully.')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('organizations:project_files', pk=pk)
    else:
        form = ProjectFileForm()
        
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == 'POST':
        # Handle form errors for AJAX
        return JsonResponse({'success': False, 'error': 'Invalid form data.'}, status=400)
        
    return render(request, 'organizations/project_files.html', {
        'project': project,
        'files': project.files.all(),
        'form': form
    })


@login_required
def project_file_delete(request, project_pk, file_pk):
    project = get_user_project_or_404(request.user, project_pk)
    project_file = get_object_or_404(ProjectFile, pk=file_pk, project=project)
    user = request.user
    
    # Check permissions: Uploader, Org Admin, or Project Manager/Creator
    can_delete = (
        project_file.uploader == user or
        user.is_admin or
        project.created_by == user or
        (user in project.members.all() and user.is_manager)
    )
    
    if not can_delete:
        messages.error(request, "You do not have permission to delete this file.")
        return redirect('organizations:project_files', pk=project_pk)
    
    if request.method == 'POST':
        project_file.delete()
        messages.success(request, 'File deleted successfully.')
        return redirect('organizations:project_files', pk=project_pk)
    
    return render(request, 'organizations/project_file_confirm_delete.html', {
        'project': project,
        'file': project_file
    })


@login_required
def project_meetings(request, pk):
    project = get_user_project_or_404(request.user, pk)
    
    if request.method == 'POST':
        form = ProjectMeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.project = project
            meeting.organizer = request.user
            meeting.save()

            # Notification logic
            from apps.accounts.models import Notification
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            channel_layer = get_channel_layer()
            
            for member in project.members.all():
                if member == request.user:
                    continue
                notification = Notification.notify(
                    recipient=member,
                    sender=request.user,
                    title=f"Meeting Scheduled: {meeting.title}",
                    content=f"New meeting for project {project.name} on {meeting.start_time.strftime('%Y-%m-%d %H:%M')}",
                    notification_type='PROJECT',
                    link=reverse('organizations:project_meetings', kwargs={'pk': project.pk})
                )
                async_to_sync(channel_layer.group_send)(
                    f"notifications_{member.id}",
                    {
                        'type': 'send_notification',
                        'id': str(notification.id),
                        'title': notification.title,
                        'content': notification.content,
                        'notification_type': notification.notification_type,
                        'link': notification.link,
                    }
                )

            messages.success(request, 'Meeting scheduled.')
            return redirect('organizations:project_meetings', pk=pk)
    else:
        form = ProjectMeetingForm()
        
    return render(request, 'organizations/project_meetings.html', {
        'project': project,
        'meetings': project.meetings.all(),
        'form': form
    })


@login_required
def project_meeting_edit(request, project_pk, meeting_pk):
    project = get_user_project_or_404(request.user, project_pk)
    meeting = get_object_or_404(ProjectMeeting, pk=meeting_pk, project=project)
    user = request.user
    
    # Check permissions: Organizer, Admin, or Project Manager/Creator
    can_edit = (
        meeting.organizer == user or
        user.is_admin or
        project.created_by == user or
        (user in project.members.all() and user.is_manager)
    )
    
    if not can_edit:
        messages.error(request, "You do not have permission to edit this meeting.")
        return redirect('organizations:project_meetings', pk=project_pk)
    
    if request.method == 'POST':
        form = ProjectMeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            meeting = form.save()
            
            # Notify members about update
            from apps.accounts.models import Notification
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            channel_layer = get_channel_layer()
            
            for member in project.members.all():
                if member == request.user: continue
                notification = Notification.notify(
                    recipient=member,
                    sender=request.user,
                    title=f"Meeting Updated: {meeting.title}",
                    content=f"Details for the meeting '{meeting.title}' have been updated.",
                    notification_type='PROJECT',
                    link=reverse('organizations:project_meetings', kwargs={'pk': project.pk})
                )
                async_to_sync(channel_layer.group_send)(
                    f"notifications_{member.id}",
                    {
                        'type': 'send_notification',
                        'id': str(notification.id),
                        'title': notification.title,
                        'content': notification.content,
                        'notification_type': notification.notification_type,
                        'link': notification.link,
                    }
                )
                
            messages.success(request, 'Meeting updated.')
            return redirect('organizations:project_meetings', pk=project_pk)
    else:
        form = ProjectMeetingForm(instance=meeting)
    
    return render(request, 'organizations/project_meeting_form.html', {
        'form': form, 
        'project': project, 
        'meeting': meeting
    })


@login_required
def project_meeting_delete(request, project_pk, meeting_pk):
    project = get_user_project_or_404(request.user, project_pk)
    meeting = get_object_or_404(ProjectMeeting, pk=meeting_pk, project=project)
    user = request.user
    
    # Check permissions
    can_delete = (
        meeting.organizer == user or
        user.is_admin or
        project.created_by == user or
        (user in project.members.all() and user.is_manager)
    )
    
    if not can_delete:
        messages.error(request, "You do not have permission to delete this meeting.")
        return redirect('organizations:project_meetings', pk=project_pk)
    
    if request.method == 'POST':
        meeting_title = meeting.title
        meeting.delete()
        
        # Notify members about cancellation
        from apps.accounts.models import Notification
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        
        for member in project.members.all():
            if member == request.user: continue
            notification = Notification.notify(
                recipient=member,
                sender=request.user,
                title=f"Meeting Cancelled: {meeting_title}",
                content=f"The meeting '{meeting_title}' has been cancelled.",
                notification_type='PROJECT',
                link=reverse('organizations:project_meetings', kwargs={'pk': project.pk})
            )
            async_to_sync(channel_layer.group_send)(
                f"notifications_{member.id}",
                {
                    'type': 'send_notification',
                    'id': str(notification.id),
                    'title': notification.title,
                    'content': notification.content,
                    'notification_type': notification.notification_type,
                    'link': notification.link,
                }
            )

        messages.success(request, 'Meeting cancelled.')
        return redirect('organizations:project_meetings', pk=project_pk)
    
    return render(request, 'organizations/project_meeting_confirm_delete.html', {
        'project': project,
        'meeting': meeting
    })


@login_required
def project_tasks(request, pk):
    project = get_user_project_or_404(request.user, pk)
    
    if request.method == 'POST':
        form = ProjectTaskForm(request.POST, project=project)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.creator = request.user
            task.save()

            # Notification logic (Notify assigned user)
            if task.assigned_to and task.assigned_to != request.user:
                from apps.accounts.models import Notification
                from asgiref.sync import async_to_sync
                from channels.layers import get_channel_layer
                channel_layer = get_channel_layer()
                
                notification = Notification.notify(
                    recipient=task.assigned_to,
                    sender=request.user,
                    title=f"New Task Assigned: {task.title}",
                    content=f"You have been assigned a task in {project.name}: {task.title}",
                    notification_type='PROJECT',
                    link=reverse('organizations:project_tasks', kwargs={'pk': project.pk})
                )
                async_to_sync(channel_layer.group_send)(
                    f"notifications_{task.assigned_to.id}",
                    {
                        'type': 'send_notification',
                        'id': str(notification.id),
                        'title': notification.title,
                        'content': notification.content,
                        'notification_type': notification.notification_type,
                        'link': notification.link,
                    }
                )

            messages.success(request, 'Task created.')
            return redirect('organizations:project_tasks', pk=pk)
    else:
        form = ProjectTaskForm(project=project)
        
    return render(request, 'organizations/project_tasks.html', {
        'project': project,
        'tasks': project.tasks.all(),
        'form': form
    })


@login_required
def project_task_edit(request, project_pk, task_pk):
    project = get_user_project_or_404(request.user, project_pk)
    task = get_object_or_404(ProjectTask, pk=task_pk, project=project)
    user = request.user
    
    # Check permissions: Admin, Manager, Project Creator, Task Creator, or Task Assignee
    can_edit = (
        user.is_admin or 
        user.is_manager or
        project.created_by == user or
        task.creator == user or
        task.assigned_to == user
    )
    
    if not can_edit:
        messages.error(request, "You do not have permission to edit this task.")
        return redirect('organizations:project_tasks', pk=project_pk)
    
    if request.method == 'POST':
        form = ProjectTaskForm(request.POST, instance=task, project=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated.')
            return redirect('organizations:project_tasks', pk=project_pk)
    else:
        form = ProjectTaskForm(instance=task, project=project)
    
    return render(request, 'organizations/project_task_form.html', {'form': form, 'project': project, 'action': 'Edit', 'task': task})


@login_required
def project_task_delete(request, project_pk, task_pk):
    project = get_user_project_or_404(request.user, project_pk)
    task = get_object_or_404(ProjectTask, pk=task_pk, project=project)
    user = request.user
    
    # Check permissions: Admin, Manager, Project Creator, or Task Creator
    can_delete = (
        user.is_admin or 
        user.is_manager or
        project.created_by == user or
        task.creator == user
    )
    
    if not can_delete:
        messages.error(request, "You do not have permission to delete this task.")
        return redirect('organizations:project_tasks', pk=project_pk)
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted.')
        return redirect('organizations:project_tasks', pk=project_pk)
    
    return render(request, 'organizations/project_task_confirm_delete.html', {'project': project, 'task': task})


@login_required
def project_analytics(request, pk):
    project = get_user_project_or_404(request.user, pk)
    if request.user not in project.members.all():
        return redirect('organizations:shared_project_list')
    
    # Gatekeeper: Check Feature Access
    if not project.host_organization.has_feature('has_analytics'):
        messages.warning(request, f"Project Analytics is a premium feature. Please upgrade the host organization's ({project.host_organization.name}) plan to gain access.")
        return redirect('organizations:shared_project_detail', pk=pk)
    
    # --- Task Stats ---
    task_stats = project.tasks.values('status').annotate(count=Count('id'))
    
    # --- Organization Activity (Collaboration Map Data) ---
    # We want to know how much each organization is contributing
    
    # Get all involved organizations (Host + Guests)
    involved_orgs = list(project.guest_organizations.all())
    involved_orgs.append(project.host_organization)
    
    org_activity = []
    
    for org in involved_orgs:
        # Members from this org in the project
        org_members = project.members.filter(organization=org)
        member_count = org_members.count()
        
        # Tasks assigned to members of this org
        tasks_assigned = project.tasks.filter(assigned_to__organization=org).count()
        tasks_completed = project.tasks.filter(assigned_to__organization=org, status='COMPLETED').count()
        
        # Files uploaded by members of this org
        files_uploaded = project.files.filter(uploader__organization=org).count()
        
        org_activity.append({
            'name': org.name,
            'member_count': member_count,
            'tasks_assigned': tasks_assigned,
            'tasks_completed': tasks_completed,
            'files_uploaded': files_uploaded,
            'score': tasks_assigned + files_uploaded + (member_count * 2) # A simple activity score for visualization sizing
        })
        
    # Sort by activity score
    org_activity.sort(key=lambda x: x['score'], reverse=True)

    # --- Top Contributors ---
    # We need to filter annotations to be specific to THIS project
    top_contributors = project.members.filter(
        # Ensure we only look at members of this project
        id__in=project.members.values('id')
    ).annotate(
        completed_task_count=Count('assigned_tasks', filter=Q(assigned_tasks__project=project, assigned_tasks__status='COMPLETED')),
        file_count=Count('projectfile', filter=Q(projectfile__project=project))
    ).order_by('-completed_task_count', '-file_count')[:5]

    context = {
        'project': project,
        'task_stats': task_stats,
        'channel_count': project.channels.count(),
        'member_count': project.members.count(),
        'org_count': project.guest_organizations.count() + 1,
        'org_activity': org_activity,
        'top_contributors': top_contributors,
    }
    return render(request, 'organizations/project_analytics.html', context)


@login_required
def shared_project_list(request):
    user = request.user
    if not user.organization:
        return redirect('accounts:dashboard')
    
    hosted_projects = SharedProject.objects.filter(host_organization=user.organization)
    guest_projects = SharedProject.objects.filter(guest_organizations=user.organization)
    my_projects = user.shared_projects.all()
    
    context = {
        'hosted_projects': hosted_projects,
        'guest_projects': guest_projects,
        'my_projects': my_projects,
    }
    return render(request, 'organizations/shared_project_list.html', context)


@login_required
def shared_project_create(request):
    user = request.user
    if not (user.is_admin or user.is_manager):
        return redirect('organizations:shared_project_list')
    
    # Gatekeeper: Check Project Limit
    if not user.organization.can_create_project():
        messages.error(request, f"Your current plan ({user.organization.get_plan().name}) only allows {user.organization.get_plan().max_projects} active project(s). Upgrade to create more.")
        return redirect('organizations:shared_project_list')

    if request.method == 'POST':
        form = SharedProjectForm(request.POST, organization=user.organization)
        if form.is_valid():
            project = form.save(commit=False)
            project.host_organization = user.organization
            project.created_by = user
            project.save()
            form.save_m2m()
            project.members.add(user)
            
            from apps.chat_channels.models import Channel
            Channel.objects.create(
                name='general',
                organization=user.organization,
                shared_project=project,
                created_by=user
            )
            
            messages.success(request, f'Project "{project.name}" created! Share code: {project.access_code}')
            return redirect('organizations:shared_project_detail', pk=project.pk)
    else:
        form = SharedProjectForm(organization=user.organization)
    
    return render(request, 'organizations/shared_project_form.html', {'form': form, 'action': 'Create'})


@login_required
def shared_project_join(request):
    user = request.user
    # Note: Removed the strict is_admin check to allow members to join projects 
    # their organization is already part of, or allow admins to link the whole org.
    
    if request.method == 'POST':
        form = JoinProjectForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['access_code']
            project = SharedProject.objects.filter(access_code=code).first()
            if project:
                # Case 1: User's org is the host
                if project.host_organization == user.organization:
                    if user in project.members.all():
                        messages.info(request, 'You are already a member of this hosted project.')
                    else:
                        project.members.add(user)
                        messages.success(request, f'You have joined the hosted project: {project.name}')
                    return redirect('organizations:shared_project_detail', pk=project.pk)
                
                # Case 2: User's org is already a guest
                elif user.organization in project.guest_organizations.all():
                    if user in project.members.all():
                        messages.info(request, 'You are already a member of this collaborative project.')
                    else:
                        project.members.add(user)
                        messages.success(request, f'You have joined the project: {project.name}')
                    return redirect('organizations:shared_project_detail', pk=project.pk)
                
                # Case 3: New organization joining (must be admin)
                else:
                    if user.is_admin:
                        project.guest_organizations.add(user.organization)
                        project.members.add(user)
                        messages.success(request, f'Your organization has successfully joined project: {project.name}')
                        return redirect('organizations:shared_project_detail', pk=project.pk)
                    else:
                        messages.error(request, 'Only organization admins can join new shared projects for the company.')
            else:
                messages.error(request, 'Invalid access code. Please check and try again.')
    else:
        form = JoinProjectForm()
    return render(request, 'organizations/shared_project_join.html', {'form': form})


@login_required
def shared_project_detail(request, pk):
    user = request.user
    project = get_user_project_or_404(request.user, pk)
    
    is_host = project.host_organization == user.organization
    is_guest = user.organization in project.guest_organizations.all()
    
    if not (is_host or is_guest):
        messages.error(request, 'You do not have access to this project.')
        return redirect('organizations:shared_project_list')
        
    # Get milestones
    milestones = project.milestones.all()
    total_milestones = milestones.count()
    completed_milestones = milestones.filter(is_completed=True).count()
    completion_percentage = int((completed_milestones / total_milestones) * 100) if total_milestones > 0 else 0
    
    # Milestone form for the foldable management section
    milestone_form = ProjectMilestoneForm()
    
    context = {
        'project': project,
        'channels': project.channels.all(),
        'members': project.members.all().select_related('organization').order_by('organization__name'),
        'milestones': milestones,
        'completion_percentage': completion_percentage,
        'milestone_form': milestone_form,
        'is_admin': user.is_admin,
        'can_manage': user.is_admin or user == project.created_by or (user in project.members.all() and user.is_manager),
        'is_member': user in project.members.all(),
        'is_host': is_host,
        'is_creator': user == project.created_by,
    }
    return render(request, 'organizations/shared_project_detail.html', context)


@login_required
def shared_project_delete(request, pk):
    """Delete a shared project. Only host organization admins or the creator can do this."""
    user = request.user
    project = get_user_project_or_404(request.user, pk)
    
    # Permission check: Host admin OR project creator
    is_host_admin = user.is_admin and project.host_organization == user.organization
    is_creator = project.created_by == user
    
    if not (is_host_admin or is_creator):
        messages.error(request, "You do not have permission to delete this project.")
        return redirect('organizations:shared_project_detail', pk=pk)
    
    if request.method == 'POST':
        project_name = project.name
        project.delete()
        messages.success(request, f'Project "{project_name}" has been successfully deleted.')
        return redirect('organizations:shared_project_list')
        
    return render(request, 'organizations/shared_project_confirm_delete.html', {'project': project})


@login_required
def organization_overview(request):
    user = request.user
    if not user.organization:
        return redirect('accounts:dashboard')
    
    departments = Department.objects.filter(organization=user.organization).prefetch_related('teams').annotate(team_count=Count('teams'))
    return render(request, 'organizations/overview.html', {'organization': user.organization, 'departments': departments})


@login_required
def department_list(request):
    user = request.user
    if not user.organization:
        return redirect('accounts:dashboard')
    
    departments = Department.objects.filter(organization=user.organization).select_related('head', 'organization').annotate(team_count=Count('teams'))
    return render(request, 'organizations/department_list.html', {'departments': departments, 'can_manage': user.is_admin or user.role == user.Role.DEPT_HEAD})


@login_required
def department_create(request):
    user = request.user
    if not user.is_admin:
        return redirect('organizations:department_list')
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, organization=user.organization)
        if form.is_valid():
            department = form.save(commit=False)
            department.organization = user.organization
            department.save()
            return redirect('organizations:department_list')
    else:
        form = DepartmentForm(organization=user.organization)
    return render(request, 'organizations/department_form.html', {'form': form, 'action': 'Create'})


@login_required
def department_edit(request, pk):
    user = request.user
    department = get_object_or_404(Department, pk=pk, organization=user.organization)
    if not (user.is_admin or department.head == user):
        return redirect('organizations:department_list')
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department, organization=user.organization)
        if form.is_valid():
            form.save()
            return redirect('organizations:department_list')
    else:
        form = DepartmentForm(instance=department, organization=user.organization)
    return render(request, 'organizations/department_form.html', {'form': form, 'action': 'Edit', 'department': department})


@login_required
def department_delete(request, pk):
    user = request.user
    department = get_object_or_404(Department, pk=pk, organization=user.organization)
    if not user.is_admin:
        return redirect('organizations:department_list')
    
    if request.method == 'POST':
        department.delete()
        return redirect('organizations:department_list')
    return render(request, 'organizations/department_confirm_delete.html', {'department': department})


@login_required
def team_list(request, department_pk=None):
    user = request.user
    if not user.organization:
        return redirect('accounts:dashboard')
    
    teams = Team.objects.filter(department__organization=user.organization).select_related('department', 'manager')
    department = get_object_or_404(Department, pk=department_pk, organization=user.organization) if department_pk else None
    if department: teams = teams.filter(department=department)
    
    return render(request, 'organizations/team_list.html', {'teams': teams, 'department': department, 'can_manage': user.is_admin or user.is_manager})


@login_required
def team_create(request, department_pk):
    user = request.user
    department = get_object_or_404(Department, pk=department_pk, organization=user.organization)
    if not (user.is_admin or user.is_manager):
        return redirect('organizations:team_list_by_dept', department_pk=department_pk)
    
    if request.method == 'POST':
        form = TeamForm(request.POST, department=department)
        if form.is_valid():
            try:
                from django.db import IntegrityError
                team = form.save(commit=False)
                team.department = department
                team.save()
                form.save_m2m()
                return redirect('organizations:team_list_by_dept', department_pk=department_pk)
            except IntegrityError:
                form.add_error('name', f'A team with this name already exists in this department.')
    else:
        form = TeamForm(department=department)
    return render(request, 'organizations/team_form.html', {'form': form, 'action': 'Create', 'department': department})


@login_required
def team_edit(request, pk):
    user = request.user
    team = get_object_or_404(Team, pk=pk, department__organization=user.organization)
    if not (user.is_admin or team.department.head == user or team.manager == user):
        return redirect('organizations:team_list_by_dept', department_pk=team.department.pk)
    
    if request.method == 'POST':
        form = TeamForm(request.POST, instance=team, department=team.department)
        if form.is_valid():
            try:
                from django.db import IntegrityError
                form.save()
                return redirect('organizations:team_list_by_dept', department_pk=team.department.pk)
            except IntegrityError:
                form.add_error('name', f'A team with this name already exists in this department.')
    else:
        form = TeamForm(instance=team, department=team.department)
    return render(request, 'organizations/team_form.html', {'form': form, 'action': 'Edit', 'team': team, 'department': team.department})


@login_required
def team_delete(request, pk):
    user = request.user
    team = get_object_or_404(Team, pk=pk, department__organization=user.organization)
    if not (user.is_admin or team.department.head == user):
        return redirect('organizations:team_list_by_dept', department_pk=team.department.pk)
    
    if request.method == 'POST':
        dept_pk = team.department.pk
        team.delete()
        return redirect('organizations:team_list_by_dept', department_pk=dept_pk)
    return render(request, 'organizations/team_confirm_delete.html', {'team': team})


@login_required
def invite_member(request):
    """Invite a new member to the organization via email."""
    user = request.user
    if not (user.is_admin or user.is_manager):
        return redirect('organizations:overview')

    # Gatekeeper: Check User Limit
    if not user.organization.can_add_user():
        messages.error(request, f"You have reached the maximum user limit for your '{user.organization.get_plan().name}' plan. Please upgrade to invite more members.")
        return redirect('organizations:member_directory')

    if request.method == 'POST':
        form = InviteMemberForm(request.POST, organization=user.organization)
        if form.is_valid():
            email = form.cleaned_data['email']
            from django.core.mail import send_mail
            from django.conf import settings
            
            invite_link = request.build_absolute_uri(f"/accounts/register/?code={user.organization.code}&email={email}")
            
            try:
                send_mail(
                    subject=f'Invitation to join {user.organization.name} on ConnectFlow',
                    message=f'You have been invited to join {user.organization.name}. Click here to join: {invite_link}',
                    from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@connectflow.com',
                    recipient_list=[email],
                    fail_silently=False,
                )
                messages.success(request, f"Invitation sent to {email}")
            except Exception as e:
                # Fallback if email is not configured
                messages.success(request, f"Please ask them to register with code: {user.organization.code}")
                # Log error in production
            
            return redirect('organizations:invite_member')
    else:
        form = InviteMemberForm(organization=user.organization)
    return render(request, 'organizations/invite_member.html', {'form': form})


@login_required
@require_POST
def member_remove(request, pk):
    user = request.user
    if not user.is_admin:
        messages.error(request, 'Only admins can remove members.')
        return redirect('organizations:member_directory')
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    member = get_object_or_404(User, pk=pk, organization=user.organization)
    
    if member == user:
        messages.error(request, "You cannot remove yourself.")
    else:
        # Clean up associations
        member.teams.clear()
        member.channels.clear()
        member.shared_projects.clear()
        
        # Remove from organization
        member.organization = None
        member.role = User.Role.TEAM_MEMBER # Reset role
        member.save()
        messages.success(request, f"{member.get_full_name() or member.username} has been removed from the organization and all its units.")
    
    return redirect('organizations:member_directory')


@login_required
def project_milestone_edit(request, project_pk, milestone_pk):
    project = get_user_project_or_404(request.user, project_pk)
    milestone = get_object_or_404(ProjectMilestone, pk=milestone_pk, project=project)
    user = request.user
    
    # Check permissions: Admin, Host Admin, Project Creator, or Dept Head/Team Manager involved
    can_edit = (
        user.is_admin or 
        project.host_organization == user.organization and user.is_admin or
        project.created_by == user or
        user in project.members.all() and (user.is_manager) 
    )
    
    if not can_edit:
        messages.error(request, "You do not have permission to edit milestones.")
        return redirect('organizations:shared_project_detail', pk=project_pk)
    
    if request.method == 'POST':
        form = ProjectMilestoneForm(request.POST, instance=milestone)
        if form.is_valid():
            form.save()
            messages.success(request, 'Milestone updated.')
            return redirect('organizations:shared_project_detail', pk=project_pk)
    else:
        form = ProjectMilestoneForm(instance=milestone)
    
    return render(request, 'organizations/project_milestone_form.html', {'form': form, 'project': project, 'action': 'Edit'})


@login_required
def project_milestone_delete(request, project_pk, milestone_pk):
    project = get_user_project_or_404(request.user, project_pk)
    milestone = get_object_or_404(ProjectMilestone, pk=milestone_pk, project=project)
    user = request.user
    
    # Check permissions: Admin, Host Admin, Project Creator, or Dept Head/Team Manager involved
    can_delete = (
        user.is_admin or 
        project.host_organization == user.organization and user.is_admin or
        project.created_by == user or
        user in project.members.all() and (user.is_manager) 
    )
    
    if not can_delete:
        messages.error(request, "You do not have permission to delete milestones.")
        return redirect('organizations:shared_project_detail', pk=project_pk)
    
    if request.method == 'POST':
        milestone.delete()
        messages.success(request, 'Milestone deleted.')
        return redirect('organizations:shared_project_detail', pk=project_pk)
    
    return render(request, 'organizations/project_milestone_confirm_delete.html', {'project': project, 'milestone': milestone})


@login_required
@require_POST
def shared_project_remove_member(request, project_pk, member_pk):
    project = get_user_project_or_404(request.user, project_pk)
    user = request.user
    
    # Check permissions
    can_remove = (
        (user.organization == project.host_organization and user.is_admin) or
        (user in project.members.all() and user.is_manager) # Allowing managers/creators to manage their project
    )
    
    if not can_remove:
         messages.error(request, "You do not have permission to remove members.")
         return redirect('organizations:shared_project_detail', pk=project_pk)
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    member_to_remove = get_object_or_404(User, pk=member_pk)
    
    if member_to_remove not in project.members.all():
         messages.error(request, "User is not in this project.")
         return redirect('organizations:shared_project_detail', pk=project_pk)
    
    # Prevent removing oneself if they are the only admin/manager? No, let them leave if they want, but here it's "remove".
    
    project.members.remove(member_to_remove)
    messages.success(request, f"{member_to_remove.get_full_name()} removed from project.")
    return redirect('organizations:shared_project_detail', pk=project_pk)


@login_required
def member_edit_role(request, pk):
    """Allow organization admins to change a member's role."""
    user = request.user
    if not user.is_admin:
        messages.error(request, "Only organization admins can change roles.")
        return redirect('organizations:member_directory')
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    member = get_object_or_404(User, pk=pk, organization=user.organization)
    
    if member == user:
        messages.error(request, "You cannot change your own role.")
        return redirect('organizations:member_directory')

    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in [r[0] for r in User.Role.choices]:
            # Security: ORG_ADMIN cannot promote someone to SUPER_ADMIN
            if new_role == User.Role.SUPER_ADMIN and user.role != User.Role.SUPER_ADMIN:
                messages.error(request, "You cannot promote users to Platform Super Admin.")
            # Gatekeeper: Check Advanced Roles (Auditor/Compliance)
            elif new_role in ['AUDITOR', 'COMPLIANCE_OFFICER'] and not user.organization.has_feature('has_advanced_roles'):
                messages.error(request, f"The Auditor and Compliance Officer roles are part of the Advanced Roles suite. Please upgrade your plan ({user.organization.get_plan().name}) to access them.")
            else:
                member.role = new_role
                # When promoting to SUPER_ADMIN, also set is_staff flag
                if new_role == User.Role.SUPER_ADMIN:
                    member.is_staff = True
                # When demoting from SUPER_ADMIN, remove is_staff flag (unless they're Django superuser)
                elif member.role == User.Role.SUPER_ADMIN and not member.is_superuser:
                    member.is_staff = False
                member.save()
                messages.success(request, f"Role for {member.get_full_name() or member.username} updated to {member.get_role_display()}.")
        else:
            messages.error(request, "Invalid role selected.")
        return redirect('organizations:member_directory')
    
    # Filter out SUPER_ADMIN role for non-superadmin org admins
    # And filter out Advanced Roles if not in plan
    has_advanced = user.organization.has_feature('has_advanced_roles')
    roles = []
    for r in User.Role.choices:
        if r[0] == User.Role.SUPER_ADMIN and user.role != User.Role.SUPER_ADMIN:
            continue
        if r[0] in ['AUDITOR', 'COMPLIANCE_OFFICER'] and not has_advanced:
            continue
        roles.append(r)

    return render(request, 'organizations/member_role_form.html', {
        'member': member,
        'roles': roles
    })


@login_required
def member_directory(request):
    user = request.user
    if not user.organization:
        return redirect('accounts:dashboard')
    
    members = user.organization.members.all().order_by('first_name', 'last_name')
    q = request.GET.get('q')
    if q: members = members.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(username__icontains=q) | Q(role__icontains=q))
    
    # Ensure is_admin is accurately passed
    is_admin = user.role == user.Role.SUPER_ADMIN or user.is_staff or user.is_superuser
    
    return render(request, 'organizations/member_directory.html', {
        'members': members, 
        'search_query': q, 
        'is_admin': is_admin
    })


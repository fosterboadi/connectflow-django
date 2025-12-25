from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Organization, Department, Team, SharedProject, ProjectFile, ProjectMeeting, ProjectTask, ProjectMilestone
from .forms import (
    DepartmentForm, TeamForm, InviteMemberForm, SharedProjectForm, JoinProjectForm,
    ProjectFileForm, ProjectMeetingForm, ProjectTaskForm, ProjectMilestoneForm
)


@login_required
def project_milestones(request, pk):
    project = get_object_or_404(SharedProject, pk=pk)
    if request.user not in project.members.all():
        return redirect('organizations:shared_project_list')
    
    if request.method == 'POST':
        form = ProjectMilestoneForm(request.POST)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.project = project
            milestone.save()
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

    if milestone.is_completed:
        from apps.accounts.models import Notification
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        
        # Notify all project members except the person who toggled it? 
        # Actually, let's notify everyone in the project.
        for member in milestone.project.members.all():
            if member == request.user:
                continue
                
            notification = Notification.notify(
                recipient=member,
                sender=request.user,
                title=f"Milestone Achieved: {milestone.title}",
                content=f"{request.user.get_full_name()} completed a milestone in {milestone.project.name}.",
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
    project = get_object_or_404(SharedProject, pk=pk)
    if request.user not in project.members.all():
        return redirect('organizations:shared_project_list')
    
    if request.method == 'POST':
        form = ProjectFileForm(request.POST, request.FILES)
        if form.is_valid():
            project_file = form.save(commit=False)
            project_file.project = project
            project_file.uploader = request.user
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
            return redirect('organizations:project_files', pk=pk)
    else:
        form = ProjectFileForm()
        
    return render(request, 'organizations/project_files.html', {
        'project': project,
        'files': project.files.all(),
        'form': form
    })


@login_required
def project_meetings(request, pk):
    project = get_object_or_404(SharedProject, pk=pk)
    if request.user not in project.members.all():
        return redirect('organizations:shared_project_list')
    
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
def project_tasks(request, pk):
    project = get_object_or_404(SharedProject, pk=pk)
    if request.user not in project.members.all():
        return redirect('organizations:shared_project_list')
    
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
def project_analytics(request, pk):
    project = get_object_or_404(SharedProject, pk=pk)
    if request.user not in project.members.all():
        return redirect('organizations:shared_project_list')
    
    task_stats = project.tasks.values('status').annotate(count=Count('id'))
    context = {
        'project': project,
        'task_stats': task_stats,
        'channel_count': project.channels.count(),
        'member_count': project.members.count(),
        'org_count': project.guest_organizations.count() + 1,
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
    # Requirement: admins, department heads, team leaders can create
    if not (user.is_admin or user.is_manager):
        messages.error(request, 'Only organization admins, department heads, and team managers can create shared projects.')
        return redirect('organizations:shared_project_list')
    
    if request.method == 'POST':
        form = SharedProjectForm(request.POST, organization=user.organization)
        if form.is_valid():
            project = form.save(commit=False)
            project.host_organization = user.organization
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
    project = get_object_or_404(SharedProject, pk=pk)
    
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
        'can_manage': user.is_admin or (user in project.members.all() and user.is_manager),
        'is_member': user in project.members.all(),
        'is_host': is_host,
    }
    return render(request, 'organizations/shared_project_detail.html', context)


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
        return redirect('organizations:team_list', department_pk=department_pk)
    
    if request.method == 'POST':
        form = TeamForm(request.POST, department=department)
        if form.is_valid():
            try:
                from django.db import IntegrityError
                team = form.save(commit=False)
                team.department = department
                team.save()
                form.save_m2m()
                return redirect('organizations:team_list', department_pk=department_pk)
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
        return redirect('organizations:team_list')
    
    if request.method == 'POST':
        form = TeamForm(request.POST, instance=team, department=team.department)
        if form.is_valid():
            try:
                from django.db import IntegrityError
                form.save()
                return redirect('organizations:team_list', department_pk=team.department.pk)
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
        return redirect('organizations:team_list')
    
    if request.method == 'POST':
        dept_pk = team.department.pk
        team.delete()
        return redirect('organizations:team_list', department_pk=dept_pk)
    return render(request, 'organizations/team_confirm_delete.html', {'team': team})


@login_required
def invite_member(request):
    user = request.user
    if not (user.is_admin or user.is_manager):
        return redirect('organizations:overview')

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
    project = get_object_or_404(SharedProject, pk=project_pk)
    milestone = get_object_or_404(ProjectMilestone, pk=milestone_pk, project=project)
    user = request.user
    
    # Check permissions: Admin, Host Admin, Project Creator, or Dept Head/Team Manager involved
    can_edit = (
        user.is_admin or 
        project.host_organization == user.organization and user.is_admin or
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
@require_POST
def shared_project_remove_member(request, project_pk, member_pk):
    project = get_object_or_404(SharedProject, pk=project_pk)
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
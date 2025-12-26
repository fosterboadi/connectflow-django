from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
from apps.accounts.models import User
from apps.organizations.models import Organization, SharedProject, SubscriptionPlan
from apps.organizations.forms import SubscriptionPlanForm

def super_admin_check(user):
    return user.is_authenticated and user.role == User.Role.SUPER_ADMIN

@login_required
@user_passes_test(super_admin_check)
def platform_plan_list(request):
    """List all available subscription plans."""
    plans = SubscriptionPlan.objects.annotate(org_count=Count('organizations'))
    return render(request, 'accounts/platform/plan_list.html', {'plans': plans})

@login_required
@user_passes_test(super_admin_check)
def platform_plan_edit(request, pk=None):
    """Create or edit a subscription plan."""
    plan = get_object_or_404(SubscriptionPlan, pk=pk) if pk else None
    
    if request.method == 'POST':
        form = SubscriptionPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, "Subscription plan updated.")
            return redirect('accounts:platform_plan_list')
    else:
        form = SubscriptionPlanForm(instance=plan)
        
    return render(request, 'accounts/platform/plan_form.html', {
        'form': form,
        'plan': plan
    })

@login_required
@user_passes_test(super_admin_check)
def platform_dashboard(request):
    """Global overview for platform operators."""
    stats = {
        'total_orgs': Organization.objects.count(),
        'active_orgs': Organization.objects.filter(is_active=True).count(),
        'total_users': User.objects.count(),
        'total_projects': SharedProject.objects.count(),
    }
    
    recent_orgs = Organization.objects.order_by('-created_at')[:5]
    recent_users = User.objects.select_related('organization').order_by('-created_at')[:5]
    
    return render(request, 'accounts/platform/dashboard.html', {
        'stats': stats,
        'recent_orgs': recent_orgs,
        'recent_users': recent_users
    })

@login_required
@user_passes_test(super_admin_check)
def platform_org_list(request):
    """Management list of all organizations."""
    query = request.GET.get('q', '')
    orgs = Organization.objects.annotate(
        member_count=Count('members', distinct=True),
        project_count=Count('hosted_projects', distinct=True)
    )
    
    if query:
        orgs = orgs.filter(Q(name__icontains=query) | Q(code__icontains=query))
    
    return render(request, 'accounts/platform/org_list.html', {
        'organizations': orgs,
        'search_query': query
    })

@login_required
@user_passes_test(super_admin_check)
def platform_user_list(request):
    """Global user directory management."""
    query = request.GET.get('q', '')
    users = User.objects.select_related('organization').all()
    
    if query:
        users = users.filter(
            Q(username__icontains=query) | 
            Q(email__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        )
    
    return render(request, 'accounts/platform/user_list.html', {
        'users_list': users,
        'search_query': query
    })

@login_required
@user_passes_test(super_admin_check)
def platform_user_permissions(request, pk):
    """Manage granular module access for a specific user."""
    target_user = get_object_or_404(User, pk=pk)
    
    modules = [
        ('dashboard', 'Dashboard Overview'),
        ('channels', 'Chat Channels'),
        ('projects', 'Shared Projects'),
        ('organization', 'Organization Overview'),
        ('members', 'Member Directory'),
        ('analytics', 'Project Analytics'),
        ('meetings', 'Project Meetings'),
        ('files', 'Project Files'),
    ]
    
    if request.method == 'POST':
        # 1. Update Global Role
        new_role = request.POST.get('role')
        if new_role in [r[0] for r in User.Role.choices]:
            target_user.role = new_role
            # If promoted to Super Admin, ensure they have staff/superuser flags for Django Admin
            if new_role == User.Role.SUPER_ADMIN:
                target_user.is_staff = True
                target_user.is_superuser = True
        
        # 2. Update Module Toggles
        new_perms = {}
        for mod_id, _ in modules:
            new_perms[mod_id] = request.POST.get(mod_id) == 'on'
        
        target_user.module_permissions = new_perms
        target_user.save()
        messages.success(request, f"Access and Role updated for {target_user.username}.")
        return redirect('accounts:platform_user_list')
        
    return render(request, 'accounts/platform/user_permissions.html', {
        'target_user': target_user,
        'modules': modules,
        'roles': User.Role.choices
    })

@login_required
@user_passes_test(super_admin_check)
def platform_toggle_org_status(request, pk):
    """Quick toggle for organization active state."""
    org = get_object_or_404(Organization, pk=pk)
    org.is_active = not org.is_active
    org.save()
    status = "activated" if org.is_active else "deactivated"
    messages.success(request, f"Organization {org.name} has been {status}.")
    return redirect('accounts:platform_org_list')

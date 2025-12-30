from django.db import models
from apps.support.models import Ticket
from apps.organizations.models import SharedProject

def get_my_tickets(user_id):
    """
    Retrieves the 5 most recent support tickets for the user.
    Returns their ID, Subject, Status, and Priority.
    """
    # Note: We pass user_id (int/str) or user object? 
    # To be safe for Gemini, we'll rely on the consumer to bind the user.
    # This function expects the actual User object to be bound via partial later, 
    # or we can assume the user is passed if we handle it manually.
    # But for "Automatic Function Calling", the AI provides the arguments.
    # The AI doesn't know the 'user' object. 
    # TRICK: We will define the actual callable in the consumer to close over 'self.user'.
    pass

# We will implement the logic as standalone functions that take a 'user' object,
# and then in the Consumer, we will wrap them so the AI doesn't need to provide the user.

def _db_get_tickets(user):
    tickets = Ticket.objects.filter(requester=user).order_by('-created_at')[:5]
    if not tickets.exists():
        return "You have no open tickets."
    
    results = []
    for t in tickets:
        results.append(f"Ticket #{str(t.id)[:8]}... | Status: {t.status} | Subject: {t.subject}")
    return "\n".join(results)

def _db_get_projects(user):
    projects = user.shared_projects.all()[:5]
    if not projects.exists():
        return "You are not listed as a member of any active shared projects."
    
    results = []
    for p in projects:
        results.append(f"Project: {p.name} (ID: {str(p.id)[:8]}) | Host: {p.host_organization.name}")
    return "\n".join(results)

def _db_get_project_milestones(user, project_id_partial):
    """Fetch milestones for a project the user belongs to."""
    # Try exact match first, then fallback to icontains
    project = user.shared_projects.filter(id__iexact=project_id_partial).first()
    if not project:
        project = user.shared_projects.filter(id__icontains=project_id_partial).first()
    
    if not project:
        # One last try by name
        project = user.shared_projects.filter(name__icontains=project_id_partial).first()

    if not project:
        return f"I couldn't find a project matching '{project_id_partial}' that you are a member of."
    
    milestones = project.milestones.all().order_by('target_date')
    if not milestones.exists():
        return f"No milestones defined for {project.name}."
    
    results = [f"Milestones for {project.name}:"]
    for m in milestones:
        status = "✅ Completed" if m.is_completed else "⏳ Pending"
        results.append(f"- {m.title} ({m.target_date}): {status}")
    return "\n".join(results)

def _db_get_upcoming_meetings(user):
    """Fetch upcoming meetings across all user projects."""
    from django.utils import timezone
    from apps.organizations.models import ProjectMeeting
    
    # Meetings in projects user is member of
    meetings = ProjectMeeting.objects.filter(
        project__members=user,
        start_time__gte=timezone.now()
    ).order_by('start_time')[:5]
    
    if not meetings.exists():
        return "You have no upcoming meetings scheduled."
    
    results = ["Your upcoming meetings:"]
    for m in meetings:
        results.append(f"- {m.title} on {m.start_time.strftime('%b %d, %I:%M %p')} (Project: {m.project.name})")
    return "\n".join(results)

def _db_get_colleagues(user):
    """List members of the user's organization and their roles."""
    if not user.organization:
        return "You are not associated with an organization."
    
    members = user.organization.members.exclude(id=user.id).order_by('last_name')[:10]
    results = [f"Colleagues at {user.organization.name}:"]
    for m in members:
        role = m.professional_role or m.get_role_display()
        results.append(f"- {m.get_full_name()} ({m.username}): {role}")
    return "\n".join(results)

def _db_find_experts(user, skill_query):
    """Find colleagues with specific skills."""
    if not user.organization:
        return "You are not associated with an organization."
    
    experts = user.organization.members.filter(skills__icontains=skill_query).exclude(id=user.id)
    if not experts.exists():
        return f"No one in {user.organization.name} has '{skill_query}' listed in their skills."
    
    results = [f"Experts in '{skill_query}':"]
    for e in experts:
        results.append(f"- {e.get_full_name()} ({e.username}): {e.skills}")
    return "\n".join(results)

def get_platform_revenue(user):
    """
    (Admin Only) Fetch the total platform revenue and recent transactions.
    """
    # 1. Security Check
    if not user.is_superuser:
        return "Access Denied: You do not have permission to view platform revenue details."

    from apps.organizations.models import SubscriptionTransaction
    from django.db.models import Sum

    # 2. Calculate Total
    total = SubscriptionTransaction.objects.aggregate(total=Sum('amount'))['total'] or 0

    # 3. Get Recent Transactions
    recent_txns = SubscriptionTransaction.objects.select_related('organization').order_by('-created_at')[:5]

    if not recent_txns.exists() and total == 0:
        return "No revenue recorded yet."

    # 4. Format Output
    response = [f"💰 Total Platform Revenue: ${total:,.2f}\n"]
    
    if recent_txns.exists():
        response.append("Recent Transactions:")
        for txn in recent_txns:
            response.append(f"- ${txn.amount} from {txn.organization.name} on {txn.created_at.strftime('%Y-%m-%d')}")
    
    return "\n".join(response)

def _db_get_tasks(user, status_filter=None):
    """Fetch tasks assigned to the user or within their projects."""
    from apps.organizations.models import ProjectTask
    tasks = ProjectTask.objects.filter(project__members=user)
    
    if status_filter:
        tasks = tasks.filter(status__icontains=status_filter)
    
    tasks = tasks.order_by('due_date')[:10]
    
    if not tasks.exists():
        return "No tasks found."
    
    results = ["Recent Tasks:"]
    for t in tasks:
        due = t.due_date.strftime('%b %d') if t.due_date else "No due date"
        results.append(f"- [{t.status}] {t.title} (Due: {due}) | Project: {t.project.name}")
    return "\n".join(results)

def _db_get_risks(user, project_name=None):
    """Fetch identified risks for a project."""
    from apps.organizations.models import ProjectRiskRegister
    risks = ProjectRiskRegister.objects.filter(project__members=user)
    
    if project_name:
        risks = risks.filter(project__name__icontains=project_name)
    
    risks = risks.order_by('-impact', '-probability')[:5]
    
    if not risks.exists():
        return "No risks found for this project."
    
    results = [f"Identified Risks:"]
    for r in risks:
        results.append(f"- {r.description} | Impact: {r.get_impact_display()} | Category: {r.get_category_display()}")
    return "\n".join(results)

def _db_get_compliance(user, project_name=None):
    """Fetch compliance requirements and their status."""
    from apps.organizations.models import ComplianceRequirement
    reqs = ComplianceRequirement.objects.filter(project__members=user)
    
    if project_name:
        reqs = reqs.filter(project__name__icontains=project_name)
    
    reqs = reqs[:10]
    
    if not reqs.exists():
        return "No compliance requirements found."
    
    results = ["Compliance Requirements:"]
    for r in reqs:
        applicable = "Yes" if r.applicable else "No"
        results.append(f"- {r.regulation} ({r.requirement_id}): {r.requirement_text[:50]}... | Applicable: {applicable}")
    return "\n".join(results)

def _db_get_project_summary(user, project_id_partial):
    """Fetch high-level analytics for a project (Completion %, Task counts)."""
    from apps.organizations.models import SharedProject
    project = user.shared_projects.filter(models.Q(id__icontains=project_id_partial) | models.Q(name__icontains=project_id_partial)).first()
    
    if not project:
        return "Project not found."
    
    total_tasks = project.tasks.count()
    completed_tasks = project.tasks.filter(status='COMPLETED').count()
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return (
        f"📊 Analytics for {project.name}:\n"
        f"- Completion Rate: {completion_rate:.1f}%\n"
        f"- Total Tasks: {total_tasks}\n"
        f"- Completed: {completed_tasks}\n"
        f"- Active Risks: {project.risks.count()}\n"
        f"- Milestones: {project.milestones.count()}"
    )

def _db_get_recent_activity(user):
    """Fetch updates from the last 7 days across user's projects."""
    from django.utils import timezone
    from datetime import timedelta
    from apps.organizations.models import ProjectTask, ProjectFile
    
    last_week = timezone.now() - timedelta(days=7)
    
    new_tasks = ProjectTask.objects.filter(project__members=user, created_at__gte=last_week).count()
    new_files = ProjectFile.objects.filter(project__members=user, created_at__gte=last_week).count()
    
    return (
        f"🕒 Recent Activity (Last 7 Days):\n"
        f"- {new_tasks} new tasks created\n"
        f"- {new_files} new files uploaded\n"
        f"- Use 'get_my_tasks' for specific details."
    )


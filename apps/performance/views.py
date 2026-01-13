"""
Views for KPI and Performance Management.

Provides both manager and member views for performance tracking.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from apps.performance.models import (
    KPIMetric, KPIAssignment, PerformanceReview, 
    PerformanceScore, PerformanceAuditLog, KPIThreshold
)
from apps.performance.services import PerformanceScoringService
from apps.performance.permissions import PerformancePermissions
from apps.accounts.models import User


# ============================================================================
# MANAGER VIEWS
# ============================================================================

@login_required
def kpi_metric_list(request):
    """List all KPI metrics for the organization (Manager view)."""
    if not PerformancePermissions.can_view_team_performance(request.user):
        return HttpResponseForbidden("You don't have permission to view KPI metrics.")
    
    metrics = KPIMetric.objects.filter(
        organization=request.user.organization,
        is_active=True
    ).select_related('team', 'created_by').order_by('-created_at')
    
    context = {
        'metrics': metrics,
        'can_create': PerformancePermissions.can_create_kpi_metric(request.user)
    }
    
    return render(request, 'performance/kpi_metric_list.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def kpi_metric_create(request):
    """Create a new KPI metric (Manager view)."""
    if not PerformancePermissions.can_create_kpi_metric(request.user):
        return HttpResponseForbidden("You don't have permission to create KPI metrics.")
    
    if request.method == 'POST':
        # Create metric from POST data
        metric = KPIMetric.objects.create(
            organization=request.user.organization,
            name=request.POST.get('name'),
            description=request.POST.get('description', ''),
            metric_type=request.POST.get('metric_type'),
            weight=Decimal(request.POST.get('weight', '1.00')),
            role=request.POST.get('role') if request.POST.get('role') else None,
            team_id=request.POST.get('team') if request.POST.get('team') else None,
            created_by=request.user
        )
        
        # Create threshold if provided
        if request.POST.get('target_value'):
            KPIThreshold.objects.create(
                metric=metric,
                min_value=request.POST.get('min_value') if request.POST.get('min_value') else None,
                target_value=Decimal(request.POST.get('target_value')),
                max_value=request.POST.get('max_value') if request.POST.get('max_value') else None,
                pass_fail_enabled=request.POST.get('pass_fail_enabled') == 'on'
            )
        
        # Log creation
        PerformanceAuditLog.log_action(
            organization=request.user.organization,
            actor=request.user,
            action=PerformanceAuditLog.ActionType.METRIC_CREATED,
            metric=metric,
            details={'name': metric.name}
        )
        
        return redirect('performance:kpi_metric_list')
    
    # GET request
    from apps.organizations.models import Team
    teams = Team.objects.filter(
        department__organization=request.user.organization
    ).select_related('department')
    
    context = {
        'teams': teams,
        'role_choices': User.Role.choices,
        'metric_type_choices': KPIMetric.MetricType.choices
    }
    
    return render(request, 'performance/kpi_metric_form.html', context)


@login_required
def assign_kpi(request):
    """Assign KPIs to users (Manager view)."""
    if not PerformancePermissions.can_view_team_performance(request.user):
        return HttpResponseForbidden("You don't have permission to assign KPIs.")
    
    if request.method == 'POST':
        metric_id = request.POST.get('metric_id')
        user_id = request.POST.get('user_id')
        review_period = request.POST.get('review_period')
        
        metric = get_object_or_404(KPIMetric, id=metric_id)
        target_user = get_object_or_404(User, id=user_id)
        
        if not PerformancePermissions.can_assign_kpi(request.user, target_user):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        assignment, created = KPIAssignment.objects.get_or_create(
            metric=metric,
            user=target_user,
            review_period=review_period,
            defaults={'assigned_by': request.user}
        )
        
        if created:
            PerformanceAuditLog.log_action(
                organization=request.user.organization,
                actor=request.user,
                action=PerformanceAuditLog.ActionType.ASSIGNMENT_CREATED,
                target_user=target_user,
                metric=metric,
                details={'review_period': review_period}
            )
        
        return JsonResponse({
            'success': True,
            'assignment_id': str(assignment.id)
        })
    
    # GET request
    metrics = KPIMetric.objects.filter(
        organization=request.user.organization,
        is_active=True
    )
    
    # Get users that can be managed
    if request.user.is_admin:
        users = User.objects.filter(organization=request.user.organization)
    elif request.user.role == User.Role.TEAM_MANAGER:
        users = User.objects.filter(teams__manager=request.user).distinct()
    else:
        users = User.objects.none()
    
    # Generate period options
    from apps.performance.utils import ReviewPeriodHelper
    try:
        current_month = ReviewPeriodHelper.get_current_period('monthly')
        next_month = ReviewPeriodHelper.get_next_period(current_month)
        current_quarter = ReviewPeriodHelper.get_current_period('quarterly')
    except Exception:
        # Fallback if period helper fails
        now = timezone.now()
        current_month = now.strftime('%Y-%m')
        next_month = (now + timedelta(days=32)).strftime('%Y-%m')
        quarter = (now.month - 1) // 3 + 1
        current_quarter = f"{now.year}-Q{quarter}"
    
    # Get pre-selected metric if provided
    selected_metric_id = request.GET.get('metric')
    selected_metric = None
    if selected_metric_id:
        try:
            selected_metric = metrics.filter(id=selected_metric_id).first()
        except Exception:
            pass
    
    context = {
        'metrics': metrics,
        'users': users,
        'current_month': current_month,
        'next_month': next_month,
        'current_quarter': current_quarter,
        'selected_metric': selected_metric
    }
    
    return render(request, 'performance/assign_kpi.html', context)


@login_required
def team_performance_overview(request):
    """Team-level performance overview (Manager view)."""
    if not PerformancePermissions.can_view_team_performance(request.user):
        return HttpResponseForbidden("You don't have permission to view team performance.")
    
    # Get reviews for the organization
    reviews = PerformanceReview.objects.filter(
        organization=request.user.organization,
        status=PerformanceReview.ReviewStatus.FINALIZED
    ).select_related('user', 'reviewer').order_by('-review_period_end')[:50]
    
    # Calculate statistics
    stats = {
        'total_reviews': reviews.count(),
        'avg_score': reviews.aggregate(Avg('final_score'))['final_score__avg'] or 0,
        'pending_reviews': PerformanceReview.objects.filter(
            organization=request.user.organization,
            status=PerformanceReview.ReviewStatus.DRAFT
        ).count()
    }
    
    context = {
        'reviews': reviews,
        'stats': stats
    }
    
    return render(request, 'performance/team_overview.html', context)


@login_required
def create_review(request):
    """Create a performance review (Manager view)."""
    if not PerformancePermissions.can_view_team_performance(request.user):
        return HttpResponseForbidden("You don't have permission to create reviews.")
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        period_start = request.POST.get('period_start')
        period_end = request.POST.get('period_end')
        
        target_user = get_object_or_404(User, id=user_id)
        
        if not PerformancePermissions.can_create_review(request.user, target_user):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        review = PerformanceReview.objects.create(
            user=target_user,
            reviewer=request.user,
            organization=request.user.organization,
            review_period_start=period_start,
            review_period_end=period_end
        )
        
        # Generate scores automatically
        PerformanceScoringService.generate_review_scores(review, request.user)
        
        # Log creation
        PerformanceAuditLog.log_action(
            organization=request.user.organization,
            actor=request.user,
            action=PerformanceAuditLog.ActionType.REVIEW_CREATED,
            target_user=target_user,
            review=review,
            details={
                'period': f"{period_start} to {period_end}"
            }
        )
        
        return JsonResponse({
            'success': True,
            'review_id': str(review.id),
            'redirect_url': f'/performance/review/{review.id}/'
        })
    
    # GET request - show form
    # Get users that can be reviewed
    if request.user.is_admin:
        users = User.objects.filter(organization=request.user.organization)
    elif request.user.role == User.Role.TEAM_MANAGER:
        users = User.objects.filter(teams__manager=request.user).distinct()
    else:
        users = User.objects.none()
    
    context = {
        'users': users
    }
    
    return render(request, 'performance/create_review.html', context)


@login_required
def review_detail(request, review_id):
    """View/edit a performance review."""
    review = get_object_or_404(
        PerformanceReview.objects.select_related('user', 'reviewer', 'organization'),
        id=review_id
    )
    
    if not PerformancePermissions.can_view_review(request.user, review):
        return HttpResponseForbidden("You don't have permission to view this review.")
    
    scores = review.scores.select_related('metric', 'overridden_by').all()
    
    context = {
        'review': review,
        'scores': scores,
        'can_edit': PerformancePermissions.can_edit_review(request.user, review),
        'can_finalize': PerformancePermissions.can_finalize_review(request.user, review)
    }
    
    return render(request, 'performance/review_detail.html', context)


@login_required
@require_http_methods(["POST"])
def override_score(request, score_id):
    """Manually override a score (Manager view)."""
    score = get_object_or_404(PerformanceScore, id=score_id)
    
    if not PerformancePermissions.can_override_score(request.user, score):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    new_score = Decimal(request.POST.get('score'))
    reason = request.POST.get('reason', '').strip()
    
    try:
        PerformanceScoringService.override_score(
            score=score,
            new_score=new_score,
            reason=reason,
            actor=request.user
        )
        
        return JsonResponse({
            'success': True,
            'new_score': str(new_score)
        })
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def finalize_review(request, review_id):
    """Finalize a performance review (Manager view)."""
    review = get_object_or_404(PerformanceReview, id=review_id)
    
    if not PerformancePermissions.can_finalize_review(request.user, review):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        PerformanceScoringService.finalize_review(review, request.user)
        
        return JsonResponse({
            'success': True,
            'final_score': str(review.final_score)
        })
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)


# ============================================================================
# MEMBER VIEWS
# ============================================================================

@login_required
def my_kpi_dashboard(request):
    """Personal KPI dashboard (Member view)."""
    # Get current assignments
    current_period = timezone.now().strftime('%Y-%m')
    
    assignments = KPIAssignment.objects.filter(
        user=request.user,
        review_period=current_period
    ).select_related('metric', 'assigned_by')
    
    # Get recent reviews
    recent_reviews = PerformanceReview.objects.filter(
        user=request.user
    ).select_related('reviewer').order_by('-review_period_end')[:5]
    
    context = {
        'assignments': assignments,
        'recent_reviews': recent_reviews,
        'current_period': current_period
    }
    
    return render(request, 'performance/my_kpi_dashboard.html', context)


@login_required
def my_performance_history(request):
    """View personal performance history (Member view)."""
    reviews = PerformanceReview.objects.filter(
        user=request.user,
        status=PerformanceReview.ReviewStatus.FINALIZED
    ).select_related('reviewer').order_by('-review_period_end')
    
    # Calculate trend data
    scores = [float(r.final_score) for r in reviews if r.final_score]
    
    context = {
        'reviews': reviews,
        'scores_data': scores,
        'average_score': sum(scores) / len(scores) if scores else 0
    }
    
    return render(request, 'performance/my_performance_history.html', context)


@login_required
def member_kpi_portfolio(request, user_id):
    """View all KPIs assigned to a specific member (Manager view)."""
    if not PerformancePermissions.can_view_team_performance(request.user):
        return HttpResponseForbidden("You don't have permission to view member portfolios.")
    
    member = get_object_or_404(User, id=user_id, organization=request.user.organization)
    
    # Check if manager can view this member
    if not PerformancePermissions.can_assign_kpi(request.user, member):
        return HttpResponseForbidden("You don't have permission to view this member's portfolio.")
    
    # Get all active KPI assignments
    assignments = KPIAssignment.objects.filter(
        user=member
    ).select_related('metric', 'assigned_by').order_by('-review_period', 'metric__name')
    
    # Group by review period
    from collections import defaultdict
    assignments_by_period = defaultdict(list)
    for assignment in assignments:
        assignments_by_period[assignment.review_period].append(assignment)
    
    # Get all reviews (draft and finalized)
    reviews = PerformanceReview.objects.filter(
        user=member
    ).select_related('reviewer').order_by('-review_period_end')
    
    # Get draft reviews
    draft_reviews = reviews.filter(status=PerformanceReview.ReviewStatus.DRAFT)
    finalized_reviews = reviews.filter(status=PerformanceReview.ReviewStatus.FINALIZED)
    
    context = {
        'member': member,
        'assignments_by_period': dict(assignments_by_period),
        'all_assignments': assignments,
        'draft_reviews': draft_reviews,
        'finalized_reviews': finalized_reviews,
        'total_kpis': assignments.count(),
    }
    
    return render(request, 'performance/member_portfolio.html', context)


@login_required
def pending_reviews_list(request):
    """List all pending (draft) reviews (Manager view)."""
    if not PerformancePermissions.can_view_team_performance(request.user):
        return HttpResponseForbidden("You don't have permission to view pending reviews.")
    
    # Get all draft reviews
    if request.user.is_admin:
        pending_reviews = PerformanceReview.objects.filter(
            organization=request.user.organization,
            status=PerformanceReview.ReviewStatus.DRAFT
        ).select_related('user', 'reviewer').order_by('-created_at')
    else:
        # Team managers only see their own drafts
        pending_reviews = PerformanceReview.objects.filter(
            reviewer=request.user,
            status=PerformanceReview.ReviewStatus.DRAFT
        ).select_related('user', 'reviewer').order_by('-created_at')
    
    context = {
        'pending_reviews': pending_reviews,
        'total_pending': pending_reviews.count()
    }
    
    return render(request, 'performance/pending_reviews.html', context)


@login_required
def my_review_detail(request, review_id):
    """View a specific review (Member view)."""
    review = get_object_or_404(
        PerformanceReview.objects.select_related('reviewer'),
        id=review_id,
        user=request.user
    )
    
    scores = review.scores.select_related('metric').all()
    
    context = {
        'review': review,
        'scores': scores,
        'is_own_review': True
    }
    
    return render(request, 'performance/review_detail.html', context)


# ============================================================================
# API ENDPOINTS
# ============================================================================

@login_required
def api_kpi_metrics(request):
    """API: Get KPI metrics (JSON)."""
    if not request.user.organization:
        return JsonResponse({'error': 'No organization'}, status=400)
    
    metrics = KPIMetric.objects.filter(
        organization=request.user.organization,
        is_active=True
    ).values('id', 'name', 'description', 'metric_type', 'weight', 'role')
    
    return JsonResponse({
        'metrics': list(metrics)
    })


@login_required
def api_my_performance(request):
    """API: Get personal performance data (JSON)."""
    reviews = PerformanceReview.objects.filter(
        user=request.user,
        status=PerformanceReview.ReviewStatus.FINALIZED
    ).order_by('-review_period_end')[:10]
    
    data = []
    for review in reviews:
        data.append({
            'id': str(review.id),
            'period_start': review.review_period_start.isoformat(),
            'period_end': review.review_period_end.isoformat(),
            'final_score': str(review.final_score) if review.final_score else None,
            'reviewer': review.reviewer.get_full_name() if review.reviewer else None,
            'comments': review.comments
        })
    
    return JsonResponse({
        'reviews': data
    })


@login_required
def api_team_performance(request):
    """API: Get team performance data (JSON)."""
    if not PerformancePermissions.can_view_team_performance(request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    reviews = PerformanceReview.objects.filter(
        organization=request.user.organization,
        status=PerformanceReview.ReviewStatus.FINALIZED
    ).select_related('user').order_by('-review_period_end')[:50]
    
    data = []
    for review in reviews:
        data.append({
            'user': review.user.get_full_name(),
            'period': f"{review.review_period_start} to {review.review_period_end}",
            'score': str(review.final_score) if review.final_score else None
        })
    
    return JsonResponse({
        'team_performance': data
    })


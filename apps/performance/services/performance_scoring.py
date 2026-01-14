"""
Performance scoring service for KPI calculation and review management.

This service handles:
- Automatic metric score calculation based on task performance
- Weighted score aggregation
- Manual score overrides with justification
- Review finalization and locking
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from django.db.models import Count, Q, Avg
from django.utils import timezone
from django.db import transaction

from apps.performance.models import (
    KPIMetric, PerformanceReview, PerformanceScore, PerformanceAuditLog, Responsibility
)
from apps.organizations.models import ProjectTask


class PerformanceScoringService:
    """Service for calculating and managing performance scores."""
    
    @staticmethod
    def calculate_metric_score(user, metric, period_start, period_end):
        """
        Calculate a score for a specific metric based on user's task performance.
        
        Returns:
            Decimal: Score from 0-100
        """
        metric_name_lower = metric.name.lower()
        
        # Get user's tasks and responsibilities in the review period
        user_tasks = ProjectTask.objects.filter(
            assigned_to=user,
            created_at__gte=period_start,
            created_at__lte=period_end
        )
        
        user_responsibilities = Responsibility.objects.filter(
            user=user,
            deadline__gte=period_start,
            deadline__lte=period_end
        )
        
        # Task Completion Rate (Includes Responsibilities)
        if 'completion' in metric_name_lower or 'completed' in metric_name_lower:
            task_score = PerformanceScoringService._calculate_completion_rate(user_tasks)
            resp_score = PerformanceScoringService._calculate_responsibility_score(user_responsibilities)
            if user_tasks.exists() and user_responsibilities.exists():
                return (task_score + resp_score) / 2
            return resp_score if user_responsibilities.exists() else task_score
        
        # Deadline Adherence (Includes Responsibilities)
        elif 'deadline' in metric_name_lower or 'on time' in metric_name_lower:
            task_score = PerformanceScoringService._calculate_deadline_adherence(user_tasks)
            resp_score = PerformanceScoringService._calculate_responsibility_deadline_score(user_responsibilities)
            if user_tasks.exists() and user_responsibilities.exists():
                return (task_score + resp_score) / 2
            return resp_score if user_responsibilities.exists() else task_score
        
        # Task Volume / Output
        elif 'volume' in metric_name_lower or 'output' in metric_name_lower:
            return PerformanceScoringService._calculate_task_volume(user_tasks, metric)
        
        # Quality (inverse of reopen rate)
        elif 'quality' in metric_name_lower or 'reopen' in metric_name_lower:
            return PerformanceScoringService._calculate_quality_score(user_tasks)
        
        # Default: return threshold target if available
        if hasattr(metric, 'threshold') and metric.threshold:
            return Decimal(str(metric.threshold.target_value))
        
        return Decimal('0.00')
    
    @staticmethod
    def _calculate_completion_rate(tasks):
        """Calculate percentage of completed tasks."""
        total_count = tasks.count()
        if total_count == 0:
            return Decimal('100.00')
        
        completed_count = tasks.filter(
            status=ProjectTask.TaskStatus.COMPLETED
        ).count()
        
        rate = (completed_count / total_count) * 100
        return Decimal(str(rate)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def _calculate_deadline_adherence(tasks):
        """Calculate percentage of tasks completed on or before deadline."""
        tasks_with_deadline = tasks.filter(due_date__isnull=False)
        total_count = tasks_with_deadline.count()
        
        if total_count == 0:
            return Decimal('100.00')
        
        on_time_count = tasks_with_deadline.filter(
            status=ProjectTask.TaskStatus.COMPLETED,
            updated_at__lte=models.F('due_date')
        ).count()
        
        rate = (on_time_count / total_count) * 100
        return Decimal(str(rate)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def _calculate_task_volume(tasks, metric):
        """
        Calculate task volume score based on threshold.
        Normalizes actual count against target.
        """
        actual_count = tasks.count()
        
        if not hasattr(metric, 'threshold') or not metric.threshold:
            return Decimal(str(min(100, actual_count * 10)))
        
        threshold = metric.threshold
        target = float(threshold.target_value)
        
        if target == 0:
            return Decimal('100.00')
        
        # Score = (actual / target) * 100, capped at 100
        score = min(100, (actual_count / target) * 100)
        return Decimal(str(score)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def _calculate_quality_score(tasks):
        """
        Calculate quality based on task stability.
        Lower reopen/modification rate = higher score.
        """
        completed_tasks = tasks.filter(status=ProjectTask.TaskStatus.COMPLETED)
        total_count = completed_tasks.count()
        
        if total_count == 0:
            return Decimal('100.00')
        
        # Tasks that went from completed back to in-progress (reopened)
        # This is a proxy; actual implementation may vary based on task history
        reopened_count = tasks.filter(
            Q(status=ProjectTask.TaskStatus.IN_PROGRESS) | 
            Q(status=ProjectTask.TaskStatus.ON_HOLD)
        ).filter(
            updated_at__gt=models.F('created_at')
        ).count()
        
        quality_rate = ((total_count - reopened_count) / total_count) * 100
        return Decimal(str(max(0, quality_rate))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def _calculate_responsibility_score(responsibilities):
        """Calculate percentage of completed responsibilities."""
        total_count = responsibilities.count()
        if total_count == 0:
            return Decimal('100.00')
        
        completed_count = responsibilities.filter(
            status=Responsibility.Status.COMPLETED
        ).count()
        
        rate = (completed_count / total_count) * 100
        return Decimal(str(rate)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @staticmethod
    def _calculate_responsibility_deadline_score(responsibilities):
        """Calculate percentage of responsibilities completed on time."""
        total_count = responsibilities.count()
        if total_count == 0:
            return Decimal('100.00')
        
        on_time_count = responsibilities.filter(
            status=Responsibility.Status.COMPLETED,
            completed_at__lte=models.F('deadline')
        ).count()
        
        rate = (on_time_count / total_count) * 100
        return Decimal(str(rate)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_final_score(review):
        """
        Calculate weighted final score for a performance review.
        
        Formula: Sum(metric_score * metric_weight) / Sum(weights)
        
        Returns:
            Decimal: Final weighted score (0-100)
        """
        scores = review.scores.select_related('metric').all()
        
        if not scores.exists():
            return Decimal('0.00')
        
        total_weighted_score = Decimal('0.00')
        total_weight = Decimal('0.00')
        
        for score in scores:
            effective_score = Decimal(str(score.get_effective_score()))
            weight = score.metric.weight
            
            total_weighted_score += effective_score * weight
            total_weight += weight
        
        if total_weight == 0:
            return Decimal('0.00')
        
        final = total_weighted_score / total_weight
        return final.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    @transaction.atomic
    def generate_review_scores(review, actor):
        """
        Generate all metric scores for a review based on KPI assignments.
        
        Args:
            review: PerformanceReview instance
            actor: User performing the action (for audit)
        
        Returns:
            list: Created PerformanceScore instances
        """
        from apps.performance.models import KPIAssignment
        from dateutil.relativedelta import relativedelta
        
        # Determine review period identifier
        review_period = f"{review.review_period_start.strftime('%Y-%m')}"
        
        # Expand dates to cover the full calendar months for scoring (Sum up for a month)
        # Start from the 1st of the start month
        full_period_start = review.review_period_start.replace(day=1)
        # End at the last day of the end month
        full_period_end = (review.review_period_end.replace(day=1) + relativedelta(months=1, days=-1))
        
        # Get all KPIs assigned to the user for this period
        assignments = KPIAssignment.objects.filter(
            user=review.user,
            review_period=review_period
        ).select_related('metric')
        
        created_scores = []
        
        for assignment in assignments:
            # Calculate score using expanded monthly boundaries
            calculated_score = PerformanceScoringService.calculate_metric_score(
                user=review.user,
                metric=assignment.metric,
                period_start=full_period_start,
                period_end=full_period_end
            )
            
            # Create or update score
            score, created = PerformanceScore.objects.update_or_create(
                review=review,
                metric=assignment.metric,
                defaults={
                    'calculated_score': calculated_score
                }
            )
            
            created_scores.append(score)
            
            # Log the calculation
            PerformanceAuditLog.log_action(
                organization=review.organization,
                actor=actor,
                action=PerformanceAuditLog.ActionType.SCORE_CALCULATED,
                target_user=review.user,
                metric=assignment.metric,
                review=review,
                details={
                    'score': str(calculated_score),
                    'review_period': review_period
                }
            )
        
        return created_scores
    
    @staticmethod
    @transaction.atomic
    def override_score(score, new_score, reason, actor):
        """
        Manually override a calculated score with justification.
        
        Args:
            score: PerformanceScore instance
            new_score: New score value (Decimal)
            reason: Justification for override (required)
            actor: User performing override
        
        Returns:
            PerformanceScore: Updated score instance
        """
        if not reason or not reason.strip():
            raise ValueError("Override reason is required")
        
        if score.review.status == PerformanceReview.ReviewStatus.FINALIZED:
            raise ValueError("Cannot override scores in finalized reviews")
        
        score.manual_override_score = new_score
        score.override_reason = reason
        score.overridden_by = actor
        score.save()
        
        # Log the override
        PerformanceAuditLog.log_action(
            organization=score.review.organization,
            actor=actor,
            action=PerformanceAuditLog.ActionType.SCORE_OVERRIDDEN,
            target_user=score.review.user,
            metric=score.metric,
            review=score.review,
            reason=reason,
            details={
                'original_score': str(score.calculated_score),
                'new_score': str(new_score)
            }
        )
        
        return score
    
    @staticmethod
    @transaction.atomic
    def finalize_review(review, actor):
        """
        Finalize a performance review, locking all scores.
        
        Args:
            review: PerformanceReview instance
            actor: User finalizing the review
        
        Returns:
            PerformanceReview: Updated review instance
        """
        if review.status == PerformanceReview.ReviewStatus.FINALIZED:
            raise ValueError("Review is already finalized")
        
        # Calculate and set final score
        final_score = PerformanceScoringService.calculate_final_score(review)
        review.final_score = final_score
        review.status = PerformanceReview.ReviewStatus.FINALIZED
        review.finalized_at = timezone.now()
        review.save()
        
        # Log finalization
        PerformanceAuditLog.log_action(
            organization=review.organization,
            actor=actor,
            action=PerformanceAuditLog.ActionType.REVIEW_FINALIZED,
            target_user=review.user,
            review=review,
            details={
                'final_score': str(final_score),
                'period': f"{review.review_period_start} to {review.review_period_end}"
            }
        )
        
        return review


# Import models for use in calculations
from django.db import models

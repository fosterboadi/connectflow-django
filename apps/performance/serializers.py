from rest_framework import serializers
from .models import (
    KPIMetric, KPIThreshold, KPIAssignment, 
    PerformanceReview, PerformanceScore, Responsibility, PerformanceAuditLog
)
from apps.accounts.serializers import UserSerializer

class KPIThresholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = KPIThreshold
        fields = ['id', 'min_value', 'target_value', 'max_value', 'pass_fail_enabled']

class KPIMetricSerializer(serializers.ModelSerializer):
    threshold = KPIThresholdSerializer(read_only=True)
    created_by_details = UserSerializer(source='created_by', read_only=True)
    team_name = serializers.ReadOnlyField(source='team.name')

    class Meta:
        model = KPIMetric
        fields = [
            'id', 'organization', 'name', 'description', 'metric_type', 
            'weight', 'role', 'team', 'team_name', 'is_active', 
            'version', 'created_by', 'created_by_details', 'created_at'
        ]

class KPIAssignmentSerializer(serializers.ModelSerializer):
    metric_details = KPIMetricSerializer(source='metric', read_only=True)
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = KPIAssignment
        fields = ['id', 'metric', 'metric_details', 'user', 'user_details', 'review_period', 'assigned_at']

class PerformanceScoreSerializer(serializers.ModelSerializer):
    metric_name = serializers.ReadOnlyField(source='metric.name')
    effective_score = serializers.ReadOnlyField(source='get_effective_score')

    class Meta:
        model = PerformanceScore
        fields = [
            'id', 'metric', 'metric_name', 'calculated_score', 
            'manual_override_score', 'override_reason', 'effective_score'
        ]

class PerformanceReviewSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    reviewer_details = UserSerializer(source='reviewer', read_only=True)
    scores = PerformanceScoreSerializer(many=True, read_only=True)

    class Meta:
        model = PerformanceReview
        fields = [
            'id', 'user', 'user_details', 'reviewer', 'reviewer_details', 
            'organization', 'review_period_start', 'review_period_end', 
            'final_score', 'status', 'comments', 'scores', 'created_at', 'finalized_at'
        ]

class ResponsibilitySerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    assigned_by_details = UserSerializer(source='assigned_by', read_only=True)

    class Meta:
        model = Responsibility
        fields = [
            'id', 'organization', 'user', 'user_details', 'assigned_by', 
            'assigned_by_details', 'title', 'description', 'deadline', 
            'status', 'completed_at', 'created_at'
        ]

class PerformanceAuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.ReadOnlyField(source='actor.username')
    target_user_name = serializers.ReadOnlyField(source='target_user.username')

    class Meta:
        model = PerformanceAuditLog
        fields = '__all__'

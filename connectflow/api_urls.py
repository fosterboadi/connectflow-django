from django.urls import path, include
from rest_framework import routers
from apps.accounts.api_views import UserViewSet, NotificationViewSet, api_login, api_logout
from apps.organizations.api_views import (
    OrganizationViewSet, DepartmentViewSet, TeamViewSet, SharedProjectViewSet,
    ProjectTaskViewSet, ProjectMilestoneViewSet, ProjectFileViewSet,
    ProjectMeetingViewSet, ProjectRiskRegisterViewSet, SubscriptionPlanViewSet,
    SubscriptionTransactionViewSet, AuditTrailViewSet, ControlTestViewSet,
    ComplianceRequirementViewSet, ComplianceEvidenceViewSet
)
from apps.chat_channels.api_views import (
    ChannelViewSet, MessageViewSet, AttachmentViewSet, 
    MessageReactionViewSet, MessageReadReceiptViewSet, 
    ChannelNotificationSettingsViewSet
)
from apps.support.api_views import TicketViewSet, TicketMessageViewSet
from apps.performance.api_views import (
    KPIMetricViewSet, KPIThresholdViewSet, KPIAssignmentViewSet, 
    PerformanceReviewViewSet, PerformanceScoreViewSet, 
    PerformanceAuditLogViewSet, ResponsibilityViewSet
)
from apps.calls.api_views import CallViewSet, CallParticipantViewSet
from apps.tools.forms.api_views import FormViewSet, FormFieldViewSet, FormResponseViewSet
from apps.tools.documents.api_views import FolderViewSet, DocumentViewSet, DocumentVersionViewSet
from apps.tools.announcements.api_views import AnnouncementViewSet, AnnouncementReadReceiptViewSet
from apps.tools.bookings.api_views import ResourceViewSet, BookingViewSet
from apps.tools.timeoff.api_views import LeaveTypeViewSet, LeaveRequestViewSet, LeaveBalanceViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'projects', SharedProjectViewSet, basename='project')
router.register(r'project-tasks', ProjectTaskViewSet, basename='project-task')
router.register(r'project-milestones', ProjectMilestoneViewSet, basename='project-milestone')
router.register(r'project-files', ProjectFileViewSet, basename='project-file')
router.register(r'project-meetings', ProjectMeetingViewSet, basename='project-meeting')
router.register(r'project-risks', ProjectRiskRegisterViewSet, basename='project-risk')
router.register(r'subscription-plans', SubscriptionPlanViewSet, basename='subscription-plan')
router.register(r'subscription-transactions', SubscriptionTransactionViewSet, basename='subscription-transaction')
router.register(r'audit-trails', AuditTrailViewSet, basename='audit-trail')
router.register(r'control-tests', ControlTestViewSet, basename='control-test')
router.register(r'compliance-requirements', ComplianceRequirementViewSet, basename='compliance-requirement')
router.register(r'compliance-evidence', ComplianceEvidenceViewSet, basename='compliance-evidence')

router.register(r'channels', ChannelViewSet, basename='channel')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'attachments', AttachmentViewSet, basename='attachment')
router.register(r'message-reactions', MessageReactionViewSet, basename='message-reaction')
router.register(r'message-read-receipts', MessageReadReceiptViewSet, basename='message-read-receipt')
router.register(r'channel-notifications', ChannelNotificationSettingsViewSet, basename='channel-notification')

router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'ticket-messages', TicketMessageViewSet, basename='ticket-message')

# Performance API
router.register(r'kpi-metrics', KPIMetricViewSet, basename='kpi-metric')
router.register(r'kpi-thresholds', KPIThresholdViewSet, basename='kpi-threshold')
router.register(r'kpi-assignments', KPIAssignmentViewSet, basename='kpi-assignment')
router.register(r'performance-reviews', PerformanceReviewViewSet, basename='performance-review')
router.register(r'performance-scores', PerformanceScoreViewSet, basename='performance-score')
router.register(r'performance-audit-logs', PerformanceAuditLogViewSet, basename='performance-audit-log')
router.register(r'responsibilities', ResponsibilityViewSet, basename='responsibility')

# Calls API
router.register(r'calls', CallViewSet, basename='call')
router.register(r'call-participants', CallParticipantViewSet, basename='call-participant')

# Corporate Tools API
router.register(r'forms', FormViewSet, basename='form')
router.register(r'form-fields', FormFieldViewSet, basename='form-field')
router.register(r'form-responses', FormResponseViewSet, basename='form-response')
router.register(r'folders', FolderViewSet, basename='folder')
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'document-versions', DocumentVersionViewSet, basename='document-version')
router.register(r'announcements', AnnouncementViewSet, basename='announcement')
router.register(r'announcement-receipts', AnnouncementReadReceiptViewSet, basename='announcement-receipt')
router.register(r'resources', ResourceViewSet, basename='resource')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'leave-types', LeaveTypeViewSet, basename='leave-type')
router.register(r'leave-requests', LeaveRequestViewSet, basename='leave-request')
router.register(r'leave-balances', LeaveBalanceViewSet, basename='leave-balance')

urlpatterns = [
    path('login/', api_login, name='api_login'),
    path('logout/', api_logout, name='api_logout'),
    path('', include(router.urls)),
]

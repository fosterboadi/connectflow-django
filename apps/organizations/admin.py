from django.contrib import admin
from .models import (
    Organization, Department, Team, SharedProject, 
    ProjectRiskRegister, AuditTrail, ControlTest, 
    ComplianceRequirement, ComplianceEvidence
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin interface for Organization model."""
    
    list_display = ('name', 'code', 'timezone', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'logo', 'description')
        }),
        ('Settings', {
            'fields': ('timezone', 'is_active')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin interface for Department model."""
    
    list_display = ('name', 'organization', 'head', 'member_count_display', 'is_active', 'created_at')
    list_filter = ('is_active', 'organization', 'created_at')
    search_fields = ('name', 'description', 'organization__name')
    readonly_fields = ('id', 'member_count_display', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'name', 'description')
        }),
        ('Management', {
            'fields': ('head', 'is_active')
        }),
        ('Metadata', {
            'fields': ('id', 'member_count_display', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def member_count_display(self, obj):
        return obj.member_count
    member_count_display.short_description = 'Total Members'


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin interface for Team model."""
    
    list_display = ('name', 'department', 'manager', 'member_count_display', 'is_active', 'created_at')
    list_filter = ('is_active', 'department__organization', 'department', 'created_at')
    search_fields = ('name', 'description', 'department__name')
    readonly_fields = ('id', 'member_count_display', 'created_at', 'updated_at')
    filter_horizontal = ('members',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('department', 'name', 'description')
        }),
        ('Management', {
            'fields': ('manager', 'members', 'is_active')
        }),
        ('Metadata', {
            'fields': ('id', 'member_count_display', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def member_count_display(self, obj):
        return obj.member_count
    member_count_display.short_description = 'Members'


@admin.register(SharedProject)
class SharedProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'host_organization', 'created_by', 'created_at')
    list_filter = ('host_organization', 'created_at')
    search_fields = ('name', 'description', 'access_code')
    filter_horizontal = ('guest_organizations', 'members')


@admin.register(ProjectRiskRegister)
class ProjectRiskRegisterAdmin(admin.ModelAdmin):
    list_display = ('project', 'category', 'probability', 'impact', 'status', 'owner')
    list_filter = ('category', 'status', 'impact')
    search_fields = ('description', 'mitigation_plan')


@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    list_display = ('project', 'audit_type', 'auditor', 'audit_date', 'risk_rating')
    list_filter = ('audit_type', 'risk_rating')
    search_fields = ('recommendations',)


@admin.register(ControlTest)
class ControlTestAdmin(admin.ModelAdmin):
    list_display = ('project', 'control_objective', 'test_result', 'tester', 'created_at')
    list_filter = ('test_result',)
    search_fields = ('control_objective', 'test_procedure')


@admin.register(ComplianceRequirement)
class ComplianceRequirementAdmin(admin.ModelAdmin):
    list_display = ('project', 'regulation', 'requirement_id', 'applicable', 'owner')
    list_filter = ('regulation', 'applicable')
    search_fields = ('requirement_id', 'requirement_text')


@admin.register(ComplianceEvidence)
class ComplianceEvidenceAdmin(admin.ModelAdmin):
    list_display = ('requirement', 'evidence_type', 'validity_period', 'review_status', 'uploaded_by')
    list_filter = ('review_status', 'evidence_type')

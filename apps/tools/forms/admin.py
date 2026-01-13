from django.contrib import admin
from .models import Form, FormField, FormResponse


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ['title', 'form_type', 'organization', 'created_by', 
                   'get_response_count', 'is_active', 'created_at']
    list_filter = ['form_type', 'is_active', 'created_at', 'organization']
    search_fields = ['title', 'description']
    readonly_fields = ['share_link', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'title', 'description', 'form_type')
        }),
        ('Access Settings', {
            'fields': ('share_link', 'is_public', 'allow_anonymous', 'require_login')
        }),
        ('Response Settings', {
            'fields': ('is_active', 'accepts_responses', 'max_responses', 'closes_at')
        }),
        ('Notifications', {
            'fields': ('send_email_on_submit', 'notification_emails'),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_response_count(self, obj):
        return obj.response_count
    get_response_count.short_description = 'Responses'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('organization', 'created_by')


@admin.register(FormField)
class FormFieldAdmin(admin.ModelAdmin):
    list_display = ['label', 'form', 'field_type', 'is_required', 'order']
    list_filter = ['field_type', 'is_required', 'form']
    search_fields = ['label', 'form__title']
    ordering = ['form', 'order']
    
    fieldsets = (
        ('Basic', {
            'fields': ('form', 'label', 'field_type', 'is_required')
        }),
        ('Display', {
            'fields': ('placeholder', 'help_text', 'order')
        }),
        ('Options (for choice fields)', {
            'fields': ('options',),
            'classes': ('collapse',)
        }),
        ('Validation', {
            'fields': ('min_value', 'max_value', 'max_length', 'pattern'),
            'classes': ('collapse',)
        }),
        ('Conditional Logic', {
            'fields': ('show_if_field', 'show_if_value'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('form')


@admin.register(FormResponse)
class FormResponseAdmin(admin.ModelAdmin):
    list_display = ['form', 'get_respondent_name', 'is_anonymous', 'submitted_at']
    list_filter = ['form', 'submitted_at', 'is_anonymous']
    search_fields = ['form__title', 'user__username', 'respondent_email']
    readonly_fields = ['form', 'user', 'answers', 'ip_address', 'user_agent', 'submitted_at']
    date_hierarchy = 'submitted_at'
    
    fieldsets = (
        ('Response Info', {
            'fields': ('form', 'user', 'is_anonymous', 'respondent_email')
        }),
        ('Answers', {
            'fields': ('answers',)
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent', 'submitted_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_respondent_name(self, obj):
        return obj.respondent_name
    get_respondent_name.short_description = 'Respondent'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('form', 'user')
    
    def has_add_permission(self, request):
        # Don't allow adding responses through admin
        return False

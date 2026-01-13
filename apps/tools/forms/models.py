from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import secrets


class Form(models.Model):
    """Custom form/survey created by users"""
    
    class FormType(models.TextChoices):
        SURVEY = 'SURVEY', _('Survey')
        FEEDBACK = 'FEEDBACK', _('Feedback Form')
        REGISTRATION = 'REGISTRATION', _('Event Registration')
        REQUEST = 'REQUEST', _('Service Request')
        ASSESSMENT = 'ASSESSMENT', _('Assessment')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='forms',
        db_index=True
    )
    
    # Basic Info
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    form_type = models.CharField(
        max_length=20,
        choices=FormType.choices,
        default=FormType.SURVEY
    )
    
    # Sharing & Access
    share_link = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text=_("Unique short URL for sharing")
    )
    is_public = models.BooleanField(
        default=False,
        help_text=_("Allow external access without login")
    )
    allow_anonymous = models.BooleanField(
        default=False,
        help_text=_("Allow anonymous responses")
    )
    require_login = models.BooleanField(
        default=True,
        help_text=_("Require user login to submit")
    )
    
    # Settings
    is_active = models.BooleanField(default=True, db_index=True)
    accepts_responses = models.BooleanField(default=True)
    max_responses = models.IntegerField(
        null=True,
        blank=True,
        help_text=_("Maximum number of responses (blank = unlimited)")
    )
    closes_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Auto-close form at this date/time")
    )
    
    # Notifications
    send_email_on_submit = models.BooleanField(default=False)
    notification_emails = models.TextField(
        blank=True,
        help_text=_("Comma-separated email addresses")
    )
    
    # Audit
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='created_forms'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'forms'
        verbose_name = _('Form')
        verbose_name_plural = _('Forms')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['created_by', '-created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Generate share link if not exists
        if not self.share_link:
            self.share_link = secrets.token_urlsafe(12)
        super().save(*args, **kwargs)
    
    @property
    def response_count(self):
        return self.responses.count()
    
    @property
    def is_accepting_responses(self):
        if not self.accepts_responses or not self.is_active:
            return False
        if self.closes_at and timezone.now() > self.closes_at:
            return False
        if self.max_responses and self.response_count >= self.max_responses:
            return False
        return True


class FormField(models.Model):
    """Individual field within a form"""
    
    class FieldType(models.TextChoices):
        SHORT_TEXT = 'SHORT_TEXT', _('Short Text')
        LONG_TEXT = 'LONG_TEXT', _('Long Text (Paragraph)')
        MULTIPLE_CHOICE = 'MULTIPLE_CHOICE', _('Multiple Choice')
        CHECKBOXES = 'CHECKBOXES', _('Checkboxes')
        DROPDOWN = 'DROPDOWN', _('Dropdown')
        NUMBER = 'NUMBER', _('Number')
        DATE = 'DATE', _('Date')
        TIME = 'TIME', _('Time')
        EMAIL = 'EMAIL', _('Email')
        PHONE = 'PHONE', _('Phone')
        FILE = 'FILE', _('File Upload')
        RATING = 'RATING', _('Rating (Stars)')
        SCALE = 'SCALE', _('Linear Scale')
        SECTION = 'SECTION', _('Section Header')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        related_name='fields'
    )
    
    # Field Configuration
    label = models.CharField(max_length=300)
    field_type = models.CharField(
        max_length=20,
        choices=FieldType.choices,
        default=FieldType.SHORT_TEXT
    )
    is_required = models.BooleanField(default=False)
    placeholder = models.CharField(max_length=200, blank=True)
    help_text = models.CharField(max_length=500, blank=True)
    
    # Options for choice-based fields (MULTIPLE_CHOICE, CHECKBOXES, DROPDOWN)
    options = models.JSONField(
        default=list,
        blank=True,
        help_text=_('List of options: ["Option 1", "Option 2"]')
    )
    
    # Validation Rules
    min_value = models.IntegerField(null=True, blank=True)
    max_value = models.IntegerField(null=True, blank=True)
    max_length = models.IntegerField(null=True, blank=True)
    pattern = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Regex pattern for validation")
    )
    
    # Conditional Logic
    show_if_field = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dependent_fields',
        help_text=_("Show this field only if another field has specific value")
    )
    show_if_value = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Value that triggers display")
    )
    
    # Ordering
    order = models.IntegerField(default=0, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'form_fields'
        verbose_name = _('Form Field')
        verbose_name_plural = _('Form Fields')
        ordering = ['order']
        indexes = [
            models.Index(fields=['form', 'order']),
        ]
    
    def __str__(self):
        return f"{self.form.title} - {self.label}"


class FormResponse(models.Model):
    """A submitted response to a form"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    
    # Respondent Information
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='form_responses'
    )
    is_anonymous = models.BooleanField(default=False)
    respondent_email = models.EmailField(
        blank=True,
        help_text=_("Email for external/anonymous respondents")
    )
    
    # Response Data
    answers = models.JSONField(
        default=dict,
        help_text=_('Field answers: {field_id: value}')
    )
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'form_responses'
        verbose_name = _('Form Response')
        verbose_name_plural = _('Form Responses')
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['form', '-submitted_at']),
            models.Index(fields=['user', '-submitted_at']),
        ]
    
    def __str__(self):
        if self.user:
            return f"{self.form.title} - {self.user.get_full_name()}"
        return f"{self.form.title} - Anonymous"
    
    @property
    def respondent_name(self):
        if self.is_anonymous:
            return "Anonymous"
        if self.user:
            return self.user.get_full_name() or self.user.username
        return self.respondent_email or "Unknown"

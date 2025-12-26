from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid
from cloudinary.models import CloudinaryField


class User(AbstractUser):
    """
    Custom User model for ConnectFlow Pro.
    Extends Django's AbstractUser to add role-based access and profile fields.
    """
    
    class Role(models.TextChoices):
        SUPER_ADMIN = 'SUPER_ADMIN', _('Super Admin')
        DEPT_HEAD = 'DEPT_HEAD', _('Department Head')
        TEAM_MANAGER = 'TEAM_MANAGER', _('Team Manager')
        TEAM_MEMBER = 'TEAM_MEMBER', _('Team Member')
    
    class Status(models.TextChoices):
        ONLINE = 'ONLINE', _('Online')
        OFFLINE = 'OFFLINE', _('Offline')
        AWAY = 'AWAY', _('Away')
        BUSY = 'BUSY', _('Busy')
    
    # Role and organization
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.TEAM_MEMBER,
        help_text=_("User's role in the organization")
    )
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='members',
        null=True,
        blank=True,
        help_text=_("Organization this user belongs to")
    )
    
    # Profile fields
    avatar = CloudinaryField(
        'avatar',
        folder='avatars',
        resource_type='auto',
        null=True,
        blank=True,
        help_text=_("User profile picture")
    )
    
    professional_role = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("e.g., Senior Software Engineer, Project Manager")
    )
    
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text=_("Short bio or description")
    )
    
    qualifications = models.TextField(
        blank=True,
        help_text=_("Certifications, degrees, or other professional qualifications")
    )
    
    skills = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Key skills, comma-separated (e.g., Python, Project Management, Agile)")
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("Contact phone number")
    )
    
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        blank=True,
        help_text=_("User's timezone")
    )

    class Theme(models.TextChoices):
        LIGHT = 'LIGHT', _('Light')
        DARK = 'DARK', _('Dark')

    theme = models.CharField(
        max_length=10,
        choices=Theme.choices,
        default=Theme.LIGHT,
        help_text=_("User's preferred theme")
    )
    
    # Status and presence
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OFFLINE,
        help_text=_("Current online status")
    )
    
    last_seen = models.DateTimeField(
        auto_now=True,
        help_text=_("Last activity timestamp")
    )
    
    # Notification preferences
    email_notifications = models.BooleanField(
        default=True,
        help_text=_("Receive email notifications")
    )
    
    mention_notifications = models.BooleanField(
        default=True,
        help_text=_("Get notified when mentioned")
    )

    # Granular Module Permissions
    module_permissions = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Toggles for platform modules: dashboard, channels, projects, organization, members, analytics")
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    def get_full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_admin(self):
        """Check if user is a Super Admin."""
        return self.role == self.Role.SUPER_ADMIN
    
    @property
    def is_manager(self):
        """Check if user is a Department Head or Team Manager."""
        return self.role in [self.Role.DEPT_HEAD, self.Role.TEAM_MANAGER]

    def has_module_access(self, module_name):
        """
        Check if user has access to a specific module.
        Super admins have access to everything.
        Default is True for all modules if not explicitly set.
        """
        if self.role == self.Role.SUPER_ADMIN:
            return True
        return self.module_permissions.get(module_name, True)


from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
import cloudinary.uploader

@receiver(pre_save, sender=User)
def delete_old_avatar_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_avatar = User.objects.get(pk=instance.pk).avatar
    except User.DoesNotExist:
        return False

    new_avatar = instance.avatar
    if old_avatar and old_avatar != new_avatar:
        try:
            cloudinary.uploader.destroy(old_avatar.public_id)
        except Exception:
            try:
                cloudinary.uploader.destroy(old_avatar.name)
            except Exception as e:
                print(f"Cloudinary cleanup error: {e}")

@receiver(post_delete, sender=User)
def delete_avatar_from_cloudinary(sender, instance, **kwargs):
    if instance.avatar:
        try:
            # For CloudinaryField, we usually use the public_id or the name
            cloudinary.uploader.destroy(instance.avatar.public_id)
        except Exception as e:
            # Native CloudinaryField might store it differently
            try:
                cloudinary.uploader.destroy(instance.avatar.name)
            except:
                print(f"Cloudinary deletion error: {e}")


class Notification(models.Model):
    """
    Notification model - tracks user alerts.
    """
    class NotificationType(models.TextChoices):
        MESSAGE = 'MESSAGE', _('New Message')
        MENTION = 'MENTION', _('Mention')
        PROJECT = 'PROJECT', _('Project Update')
        CHANNEL = 'CHANNEL', _('Channel Activity')
        MEMBERSHIP = 'MEMBERSHIP', _('Membership Update')
        SYSTEM = 'SYSTEM', _('System Alert')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices, default=NotificationType.SYSTEM)
    title = models.CharField(max_length=255)
    content = models.TextField()
    link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type} for {self.recipient.username}"

    @classmethod
    def notify(cls, recipient, title, content, notification_type='SYSTEM', sender=None, link=None):
        """Create a notification record in the database."""
        return cls.objects.create(
            recipient=recipient,
            sender=sender,
            title=title,
            content=content,
            notification_type=notification_type,
            link=link
        )

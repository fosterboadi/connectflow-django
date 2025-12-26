from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from cloudinary.models import CloudinaryField


class Organization(models.Model):
    """
    Organization model - represents a company or organization.
    Each user belongs to one organization.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text=_("Organization name")
    )
    
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text=_("Unique organization code for signup")
    )
    
    logo = CloudinaryField(
        'logo',
        folder='organizations/logos',
        resource_type='auto',
        null=True,
        blank=True,
        help_text=_("Organization logo")
    )
    
    description = models.TextField(
        blank=True,
        help_text=_("Organization description")
    )

    class Industry(models.TextChoices):
        TECHNOLOGY = 'TECH', _('Technology')
        FINANCE = 'FIN', _('Finance & Banking')
        HEALTHCARE = 'HEALTH', _('Healthcare')
        EDUCATION = 'EDU', _('Education')
        MANUFACTURING = 'MANU', _('Manufacturing')
        RETAIL = 'RETAIL', _('Retail & E-commerce')
        CONSULTING = 'CONSULT', _('Consulting')
        OTHER = 'OTHER', _('Other')

    industry = models.CharField(
        max_length=20,
        choices=Industry.choices,
        default=Industry.OTHER,
        help_text=_("Primary industry")
    )

    website = models.URLField(
        blank=True,
        null=True,
        help_text=_("Official website URL")
    )

    size = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Company size (e.g., 10-50 employees)")
    )

    headquarters = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_("HQ Location (City, Country)")
    )
    
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        help_text=_("Organization default timezone")
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text=_("Is this organization active?")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'organizations'
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Department(models.Model):
    """
    Department model - represents departments within an organization.
    Example: Engineering, Sales, Marketing, HR
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='departments',
        help_text=_("Organization this department belongs to")
    )
    
    name = models.CharField(
        max_length=200,
        help_text=_("Department name")
    )
    
    description = models.TextField(
        blank=True,
        help_text=_("Department description")
    )
    
    head = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments',
        help_text=_("Department head")
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text=_("Is this department active?")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'departments'
        verbose_name = _('Department')
        verbose_name_plural = _('Departments')
        ordering = ['organization', 'name']
        unique_together = [['organization', 'name']]
    
    def __str__(self):
        return f"{self.name} ({self.organization.name})"
    
    @property
    def member_count(self):
        """Return total number of members in all teams under this department."""
        return sum(team.members.count() for team in self.teams.all())


class Team(models.Model):
    """
    Team model - represents teams within departments.
    Example: Backend Team, Frontend Team, Sales Team A
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='teams',
        help_text=_("Department this team belongs to")
    )
    
    name = models.CharField(
        max_length=200,
        help_text=_("Team name")
    )
    
    description = models.TextField(
        blank=True,
        help_text=_("Team description")
    )
    
    manager = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_teams',
        help_text=_("Team manager")
    )
    
    members = models.ManyToManyField(
        'accounts.User',
        related_name='teams',
        blank=True,
        help_text=_("Team members")
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text=_("Is this team active?")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'teams'
        verbose_name = _('Team')
        verbose_name_plural = _('Teams')
        ordering = ['department', 'name']
        unique_together = [['department', 'name']]
    
    def __str__(self):
        return f"{self.name} ({self.department.name})"
    
    @property
    def member_count(self):
        """Return number of members in this team."""
        return self.members.count()
    
    @property
    def organization(self):
        """Get the organization through the department."""
        return self.department.organization


class SharedProject(models.Model):
    """
    SharedProject model - connects multiple organizations for collaboration.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    name = models.CharField(
        max_length=200,
        help_text=_("Project name")
    )
    
    description = models.TextField(
        blank=True,
        help_text=_("Project description")
    )
    
    host_organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='hosted_projects',
        help_text=_("Organization that owns this project")
    )
    
    guest_organizations = models.ManyToManyField(
        Organization,
        related_name='guest_projects',
        blank=True,
        help_text=_("Organizations invited to collaborate")
    )
    
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_projects',
        help_text=_("User who created this project")
    )
    
    members = models.ManyToManyField(
        'accounts.User',
        related_name='shared_projects',
        blank=True,
        help_text=_("Selected members from all organizations involved")
    )
    
    access_code = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text=_("Code for other organizations to join")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'shared_projects'
        verbose_name = _('Shared Project')
        verbose_name_plural = _('Shared Projects')
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.access_code:
            import secrets
            import string
            # Generate a readable but secure code: PROJECT-XXXX-XXXX
            alphabet = string.ascii_uppercase + string.digits
            code = ''.join(secrets.choice(alphabet) for _ in range(8))
            self.access_code = f"PROJ-{code[:4]}-{code[4:]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (Hosted by {self.host_organization.name})"


class ProjectFile(models.Model):
    """Files shared specifically within a shared project."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(SharedProject, on_delete=models.CASCADE, related_name='files')
    uploader = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    file = models.FileField(
        upload_to='projects/files',
        help_text=_("Shared file")
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class ProjectMeeting(models.Model):
    """Meetings scheduled for a shared project."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(SharedProject, on_delete=models.CASCADE, related_name='meetings')
    organizer = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    meeting_link = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_time']


class ProjectTask(models.Model):
    """Tasks assigned within a shared project."""
    class TaskStatus(models.TextChoices):
        TODO = 'TODO', _('To Do')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        COMPLETED = 'COMPLETED', _('Completed')
        ON_HOLD = 'ON_HOLD', _('On Hold')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(SharedProject, on_delete=models.CASCADE, related_name='tasks')
    creator = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='created_tasks')
    assigned_to = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=TaskStatus.choices, default=TaskStatus.TODO)
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', 'created_at']


class ProjectMilestone(models.Model):
    """Key milestones for a shared project to track progress."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(SharedProject, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    target_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['target_date']

    def __str__(self):
        return f"{self.title} - {self.project.name}"


from django.db.models.signals import m2m_changed, post_delete, pre_save
from django.dispatch import receiver
from django.urls import reverse
import cloudinary.uploader

@receiver(pre_save, sender=Organization)
def delete_old_org_logo_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_logo = Organization.objects.get(pk=instance.pk).logo
    except Organization.DoesNotExist:
        return False

    new_logo = instance.logo
    if old_logo and old_logo != new_logo:
        try:
            cloudinary.uploader.destroy(old_logo.public_id)
        except Exception:
            try:
                cloudinary.uploader.destroy(old_logo.name)
            except Exception as e:
                print(f"Cloudinary cleanup error: {e}")

@receiver(post_delete, sender=Organization)
def delete_org_logo_from_cloudinary(sender, instance, **kwargs):
    if instance.logo:
        try:
            cloudinary.uploader.destroy(instance.logo.public_id)
        except Exception as e:
            try:
                cloudinary.uploader.destroy(instance.logo.name)
            except:
                print(f"Cloudinary deletion error: {e}")

@receiver(post_delete, sender=ProjectFile)
def delete_project_file_from_cloudinary(sender, instance, **kwargs):
    if instance.file:
        try:
            # This calls the storage backend's delete method (RawMediaCloudinaryStorage)
            instance.file.delete(save=False)
        except Exception as e:
            print(f"File deletion error: {e}")

@receiver(m2m_changed, sender=Team.members.through)
def notify_members_added_to_team(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        from apps.accounts.models import Notification, User
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        
        channel_layer = get_channel_layer()
        
        for user_id in pk_set:
            try:
                user = User.objects.get(pk=user_id)
                # Team managers often add users, but we'll use instance manager if set
                sender_user = instance.manager
                
                notification = Notification.notify(
                    recipient=user,
                    sender=sender_user,
                    title=f"Joined Team: {instance.name}",
                    content=f"You have been added to the team {instance.name}.",
                    notification_type='MEMBERSHIP',
                    link=reverse('organizations:overview') # Link to org overview where teams are listed
                )
                
                # Broadcast via WebSocket
                async_to_sync(channel_layer.group_send)(
                    f"notifications_{user.id}",
                    {
                        'type': 'send_notification',
                        'id': str(notification.id),
                        'title': notification.title,
                        'content': notification.content,
                        'notification_type': notification.notification_type,
                        'link': notification.link,
                    }
                )
            except Exception as e:
                print(f"Error sending notification: {e}")

@receiver(m2m_changed, sender=SharedProject.members.through)
def notify_members_added_to_project(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        from apps.accounts.models import Notification, User
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        
        channel_layer = get_channel_layer()
        
        for user_id in pk_set:
            try:
                user = User.objects.get(pk=user_id)
                # We don't have a clear "creator" but we can use project name
                link = reverse('organizations:shared_project_detail', kwargs={'pk': instance.pk})
                notification = Notification.notify(
                    recipient=user,
                    sender=instance.created_by if hasattr(instance, 'created_by') else None,
                    title=f"Joined Project: {instance.name}",
                    content=f"You have been added to the shared project {instance.name}.",
                    notification_type='PROJECT',
                    link=link
                )
                
                # Broadcast via WebSocket
                async_to_sync(channel_layer.group_send)(
                    f"notifications_{user.id}",
                    {
                        'type': 'send_notification',
                        'id': str(notification.id),
                        'title': notification.title,
                        'content': notification.content,
                        'notification_type': notification.notification_type,
                        'link': notification.link,
                    }
                )
            except Exception as e:
                print(f"Error sending notification: {e}")

from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


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
    
    logo = models.ImageField(
        upload_to='organizations/logos/',
        null=True,
        blank=True,
        help_text=_("Organization logo")
    )
    
    description = models.TextField(
        blank=True,
        help_text=_("Organization description")
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
        limit_choices_to={'role': 'DEPT_HEAD'},
        help_text=_("Department head (must have DEPT_HEAD role)")
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
        limit_choices_to={'role__in': ['TEAM_MANAGER', 'DEPT_HEAD']},
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
    file = models.FileField(upload_to='projects/files/%Y/%m/%d/')
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

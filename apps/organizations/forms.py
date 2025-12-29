from django import forms
from django.contrib.auth import get_user_model
from .models import (
    Organization, Department, Team, SharedProject, ProjectFile, 
    ProjectMeeting, ProjectTask, ProjectMilestone, SubscriptionPlan,
    ProjectRiskRegister, AuditTrail, ControlTest, ComplianceRequirement, ComplianceEvidence
)

User = get_user_model()


class ProjectRiskForm(forms.ModelForm):
    class Meta:
        model = ProjectRiskRegister
        fields = ['category', 'description', 'probability', 'impact', 'mitigation_plan', 'owner', 'status']
        widgets = {
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900', 'rows': 2}),
            'probability': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900'}),
            'impact': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900'}),
            'mitigation_plan': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900', 'rows': 2}),
            'owner': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900'}),
            'status': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900'}),
        }

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        if project:
            self.fields['owner'].queryset = project.members.all()


class AuditTrailForm(forms.ModelForm):
    class Meta:
        model = AuditTrail
        fields = ['audit_type', 'audit_date', 'findings', 'recommendations', 'risk_rating', 'follow_up_date']
        widgets = {
            'audit_type': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900'}),
            'audit_date': forms.DateTimeInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900', 'type': 'datetime-local'}),
            'findings': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900', 'rows': 3, 'placeholder': 'Enter findings as a JSON list or plain text...'}),
            'recommendations': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900', 'rows': 2}),
            'risk_rating': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900'}),
            'follow_up_date': forms.DateInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900', 'type': 'date'}),
        }


class ControlTestForm(forms.ModelForm):
    class Meta:
        model = ControlTest
        fields = ['control_objective', 'test_procedure', 'sample_size', 'exceptions_found', 'test_result', 'evidence_reference']
        widgets = {
            'control_objective': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900'}),
            'test_procedure': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900', 'rows': 2}),
            'sample_size': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900'}),
            'exceptions_found': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900'}),
            'test_result': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900'}),
            'evidence_reference': forms.URLInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900', 'placeholder': 'https://...'}),
        }


class ComplianceEvidenceForm(forms.ModelForm):
    class Meta:
        model = ComplianceEvidence
        fields = ['evidence_type', 'document', 'validity_period']
        widgets = {
            'evidence_type': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900', 'placeholder': 'e.g., Audit Log, Policy Document'}),
            'document': forms.FileInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'validity_period': forms.DateInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900', 'type': 'date'}),
        }


class SubscriptionPlanForm(forms.ModelForm):
    storage_value = forms.FloatField(
        label="Storage Limit",
        widget=forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-indigo-500', 'step': '0.1'})
    )
    storage_unit = forms.ChoiceField(
        choices=[('MB', 'MB'), ('GB', 'GB'), ('TB', 'TB')],
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-indigo-500'})
    )

    class Meta:
        model = SubscriptionPlan
        fields = [
            'name', 'price_monthly', 'paystack_plan_code',
            'max_users', 'max_projects', 'max_storage_mb', 
            'has_analytics', 'has_custom_branding', 
            'has_priority_support', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-indigo-500'}),
            'price_monthly': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-indigo-500'}),
            'paystack_plan_code': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-indigo-500', 'placeholder': 'PLN_...'}),
            'max_users': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-indigo-500', 'placeholder': '-1 for unlimited'}),
            'max_projects': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-indigo-500', 'placeholder': '-1 for unlimited'}),
            'max_storage_mb': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Convert MB back to appropriate unit for display
            mb = self.instance.max_storage_mb
            if mb >= 1048576:
                self.fields['storage_value'].initial = round(mb / 1048576, 2)
                self.fields['storage_unit'].initial = 'TB'
            elif mb >= 1024:
                self.fields['storage_value'].initial = round(mb / 1024, 2)
                self.fields['storage_unit'].initial = 'GB'
            else:
                self.fields['storage_value'].initial = mb
                self.fields['storage_unit'].initial = 'MB'

    def clean(self):
        cleaned_data = super().clean()
        val = cleaned_data.get('storage_value')
        unit = cleaned_data.get('storage_unit')

        if val is not None and unit:
            if unit == 'GB':
                cleaned_data['max_storage_mb'] = int(val * 1024)
            elif unit == 'TB':
                cleaned_data['max_storage_mb'] = int(val * 1024 * 1024)
            else:
                cleaned_data['max_storage_mb'] = int(val)
        
        return cleaned_data


class OrganizationForm(forms.ModelForm):
    """Form for editing organization details."""
    
    class Meta:
        model = Organization
        fields = ['name', 'logo', 'description', 'industry', 'website', 'size', 'headquarters', 'timezone']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
            }),
            'logo': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'rows': 3
            }),
            'industry': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
            }),
            'website': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'https://example.com'
            }),
            'size': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'e.g., 50-100 employees'
            }),
            'headquarters': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'e.g., London, UK'
            }),
            'timezone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
            }),
        }


class ProjectMilestoneForm(forms.ModelForm):
    class Meta:
        model = ProjectMilestone
        fields = ['title', 'description', 'target_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900', 'rows': 2}),
            'target_date': forms.DateInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900', 'type': 'date'}),
        }


class ProjectFileForm(forms.ModelForm):
    class Meta:
        model = ProjectFile
        fields = ['file', 'name', 'description']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'placeholder': 'File display name'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'rows': 2}),
        }


class ProjectMeetingForm(forms.ModelForm):
    class Meta:
        model = ProjectMeeting
        fields = ['title', 'description', 'start_time', 'end_time', 'meeting_link']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'rows': 2}),
            'start_time': forms.DateTimeInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'type': 'datetime-local'}),
            'meeting_link': forms.URLInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'placeholder': 'https://...'}),
        }


class ProjectTaskForm(forms.ModelForm):
    class Meta:
        model = ProjectTask
        fields = ['title', 'description', 'assigned_to', 'status', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900', 'rows': 2}),
            'assigned_to': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900'}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900', 'type': 'datetime-local'}),
        }

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        if project:
            self.fields['assigned_to'].queryset = project.members.all()


class SharedProjectForm(forms.ModelForm):
    """Form for creating a shared project."""
    class Meta:
        model = SharedProject
        fields = ['name', 'description', 'members']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'e.g., Joint Venture - Alpha'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'Explain the collaboration goals...',
                'rows': 3
            }),
            'members': forms.CheckboxSelectMultiple(attrs={
                'class': 'grid grid-cols-1 md:grid-cols-2 gap-2 max-h-60 overflow-y-auto p-4 border rounded-lg bg-gray-50'
            })
        }

    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)
        if organization:
            # Initially, only members of the host org can be selected
            # More can be added later as guest orgs join
            self.fields['members'].queryset = User.objects.filter(organization=organization)

    def save(self, commit=True):
        project = super().save(commit=False)
        if commit:
            project.save()
            self.save_m2m() # This will set members correctly (existing + newly checked)
        return project


class JoinProjectForm(forms.Form):
    """Form for joining a shared project via code."""
    access_code = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
            'placeholder': 'e.g., PROJ-XXXX-XXXX'
        })
    )


class DepartmentForm(forms.ModelForm):
    """Form for creating and editing departments."""
    
    class Meta:
        model = Department
        fields = ['name', 'description', 'head', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'e.g., Engineering, Sales, Marketing'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'Department description...',
                'rows': 3
            }),
            'head': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'
            })
        }
    
    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter department heads to show all users from the same organization
        if organization:
            self.fields['head'].queryset = User.objects.filter(
                organization=organization
            )
        else:
            self.fields['head'].queryset = User.objects.all()
        
        # Make head field optional
        self.fields['head'].required = False

    def save(self, commit=True):
        department = super().save(commit=False)
        if department.head:
            # Promote the selected user to DEPT_HEAD if they aren't already an admin
            if department.head.role not in [User.Role.SUPER_ADMIN, User.Role.DEPT_HEAD]:
                department.head.role = User.Role.DEPT_HEAD
                department.head.save()
                
                # Notify the user of their promotion
                from apps.accounts.models import Notification
                from asgiref.sync import async_to_sync
                from channels.layers import get_channel_layer
                from django.urls import reverse
                
                channel_layer = get_channel_layer()
                notification = Notification.notify(
                    recipient=department.head,
                    title="Role Promotion",
                    content=f"You have been promoted to Department Head for {department.name}.",
                    notification_type='MEMBERSHIP',
                    link=reverse('organizations:department_list')
                )
                
                async_to_sync(channel_layer.group_send)(
                    f"notifications_{department.head.id}",
                    {
                        'type': 'send_notification',
                        'id': str(notification.id),
                        'title': notification.title,
                        'content': notification.content,
                        'notification_type': notification.notification_type,
                        'link': notification.link,
                    }
                )
        
        if commit:
            department.save()
        return department


class TeamForm(forms.ModelForm):
    """Form for creating and editing teams."""
    
    class Meta:
        model = Team
        fields = ['name', 'description', 'manager', 'members', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'e.g., Backend Team, Sales Team A'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'Team description...',
                'rows': 3
            }),
            'manager': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent'
            }),
            'members': forms.CheckboxSelectMultiple(attrs={
                'class': 'grid grid-cols-1 md:grid-cols-2 gap-2 max-h-60 overflow-y-auto p-4 border rounded-lg bg-gray-50'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'
            })
        }
    
    def __init__(self, *args, department=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.department = department
        
        # Filter managers and members based on department's organization
        if department:
            organization = department.organization
            
            # Managers can be any user from same organization
            self.fields['manager'].queryset = User.objects.filter(
                organization=organization
            )
            
            # Members can be any user from the same organization
            self.fields['members'].queryset = User.objects.filter(
                organization=organization
            )
        else:
            self.fields['manager'].queryset = User.objects.all()
            self.fields['members'].queryset = User.objects.all()
        
        # Make fields optional
        self.fields['manager'].required = False
        self.fields['members'].required = False

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        
        if name and self.department:
            # Check if a team with this name already exists in this department
            # Exclude current instance if editing
            query = Team.objects.filter(department=self.department, name=name)
            if self.instance.pk:
                query = query.exclude(pk=self.instance.pk)
            
            if query.exists():
                self.add_error('name', f'A team named "{name}" already exists in this department.')
        
        return cleaned_data

    def save(self, commit=True):
        team = super().save(commit=False)
        if team.manager:
            if team.manager.role == User.Role.TEAM_MEMBER:
                team.manager.role = User.Role.TEAM_MANAGER
                team.manager.save()
                
                # Notify the user of their promotion
                from apps.accounts.models import Notification
                from asgiref.sync import async_to_sync
                from channels.layers import get_channel_layer
                from django.urls import reverse
                
                channel_layer = get_channel_layer()
                notification = Notification.notify(
                    recipient=team.manager,
                    title="Role Promotion",
                    content=f"You have been promoted to Team Manager for {team.name}.",
                    notification_type='MEMBERSHIP',
                    link=reverse('organizations:overview')
                )
                
                async_to_sync(channel_layer.group_send)(
                    f"notifications_{team.manager.id}",
                    {
                        'type': 'send_notification',
                        'id': str(notification.id),
                        'title': notification.title,
                        'content': notification.content,
                        'notification_type': notification.notification_type,
                        'link': notification.link,
                    }
                )
        
        if commit:
            team.save()
            self.save_m2m() # Standard Django behavior handles the selection correctly
        return team


class InviteMemberForm(forms.Form):
    """Form for inviting a new member."""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
            'placeholder': 'Enter email to send invitation'
        })
    )

    def __init__(self, *args, organization=None, **kwargs):
        self.organization = organization
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        if self.organization and User.objects.filter(organization=self.organization, email=email).exists():
            raise forms.ValidationError('A user with this email already exists in this organization.')
        return email

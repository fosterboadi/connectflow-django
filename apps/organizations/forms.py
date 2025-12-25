from django import forms
from django.contrib.auth import get_user_model
from .models import (
    Organization, Department, Team, SharedProject, ProjectFile, 
    ProjectMeeting, ProjectTask, ProjectMilestone
)

User = get_user_model()


class ProjectMilestoneForm(forms.ModelForm):
    class Meta:
        model = ProjectMilestone
        fields = ['title', 'description', 'target_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'rows': 2}),
            'target_date': forms.DateInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'type': 'date'}),
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
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'rows': 2}),
            'assigned_to': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'type': 'datetime-local'}),
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

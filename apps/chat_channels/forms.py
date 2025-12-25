from django import forms
from django.contrib.auth import get_user_model
from .models import Channel, Message
from apps.organizations.models import Department, Team, SharedProject

User = get_user_model()


class ChannelForm(forms.ModelForm):
    """Form for creating and editing channels."""
    
    class Meta:
        model = Channel
        fields = ['name', 'description', 'channel_type', 'department', 'team', 'members', 'is_private', 'read_only', 'shared_project']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'e.g., general, announcements, project-alpha'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'Channel description...',
                'rows': 3
            }),
            'channel_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent'
            }),
            'department': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent'
            }),
            'team': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent'
            }),
            'members': forms.CheckboxSelectMultiple(attrs={
                'class': 'grid grid-cols-1 md:grid-cols-2 gap-2 max-h-60 overflow-y-auto p-4 border rounded-lg bg-gray-50'
            }),
            'is_private': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'
            }),
            'read_only': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'
            }),
            'shared_project': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent'
            })
        }
    
    def __init__(self, *args, organization=None, shared_project=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if organization:
            self.fields['department'].queryset = Department.objects.filter(organization=organization)
            self.fields['team'].queryset = Team.objects.filter(department__organization=organization)
            
            if shared_project:
                self.fields['members'].queryset = shared_project.members.all()
                self.fields['shared_project'].queryset = SharedProject.objects.filter(id=shared_project.id)
                self.fields['shared_project'].initial = shared_project
            else:
                self.fields['members'].queryset = User.objects.filter(organization=organization)
                self.fields['shared_project'].queryset = SharedProject.objects.filter(host_organization=organization)
        else:
            self.fields['department'].queryset = Department.objects.none()
            self.fields['team'].queryset = Team.objects.none()
            self.fields['members'].queryset = User.objects.none()
            self.fields['shared_project'].queryset = SharedProject.objects.none()
        
        self.fields['department'].required = False
        self.fields['team'].required = False
        self.fields['members'].required = False
        self.fields['shared_project'].required = False

    def save(self, commit=True):
        channel = super().save(commit=False)
        if commit:
            channel.save()
            self.save_m2m() # This handles the 'members' field correctly

            # Auto-add team members if team is selected (even if not checked in members field)
            if channel.team:
                channel.members.add(*channel.team.members.all())
            
            # Auto-add department members if department is selected
            if channel.department:
                for team in channel.department.teams.all():
                    channel.members.add(*team.members.all())
                    
        return channel


class MessageForm(forms.ModelForm):
    """Form for sending messages in channels."""
    
    class Meta:
        model = Message
        fields = ['content', 'voice_message', 'voice_duration', 'parent_message']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'Type your message... (Shift+Enter for new line)',
                'rows': 3
            }),
            'voice_message': forms.FileInput(attrs={'id': 'voice-message-input', 'class': 'hidden'}),
            'voice_duration': forms.HiddenInput(attrs={'id': 'voice-duration-input'}),
            'parent_message': forms.HiddenInput()
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = False
        self.fields['voice_message'].required = False
        self.fields['voice_duration'].required = False
        self.fields['parent_message'].required = False


class BreakoutRoomForm(forms.ModelForm):
    """Form for creating breakout rooms."""
    
    class Meta:
        model = Channel
        fields = ['name', 'description', 'members']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'e.g., Quick sync, Brainstorming'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'Topic of discussion...',
                'rows': 3
            }),
            'members': forms.SelectMultiple(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'size': '5'
            }),
        }
    
    def __init__(self, *args, parent_channel=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if parent_channel:
            organization = parent_channel.organization
            qs = User.objects.filter(organization=organization)
            
            if parent_channel.channel_type == Channel.ChannelType.TEAM and parent_channel.team:
                qs = qs.filter(teams=parent_channel.team)
            elif parent_channel.channel_type == Channel.ChannelType.DEPARTMENT and parent_channel.department:
                 qs = qs.filter(teams__department=parent_channel.department).distinct()
            elif parent_channel.channel_type == Channel.ChannelType.PRIVATE:
                qs = parent_channel.members.all()
            elif parent_channel.channel_type == Channel.ChannelType.DIRECT:
                 qs = parent_channel.members.all()

            self.fields['members'].queryset = qs

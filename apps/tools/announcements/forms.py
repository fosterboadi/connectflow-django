from django import forms
from .models import Announcement

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = [
            'title', 'content', 'priority', 'target_department', 
            'target_team', 'target_role', 'scheduled_at', 
            'expires_at', 'require_acknowledgement', 'is_pinned'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-5 py-4 bg-gray-50 border-none rounded-2xl text-base font-medium focus:ring-2 focus:ring-blue-500 transition-all',
                'placeholder': 'What is this about?'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-5 py-4 bg-gray-50 border-none rounded-2xl text-base font-medium focus:ring-2 focus:ring-blue-500 transition-all',
                'rows': 6,
                'placeholder': 'Write your announcement details here...'
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full px-5 py-4 bg-gray-50 border-none rounded-2xl text-base font-medium focus:ring-2 focus:ring-blue-500 transition-all'
            }),
            'target_department': forms.Select(attrs={
                'class': 'w-full px-5 py-4 bg-gray-50 border-none rounded-2xl text-base font-medium focus:ring-2 focus:ring-blue-500 transition-all'
            }),
            'target_team': forms.Select(attrs={
                'class': 'w-full px-5 py-4 bg-gray-50 border-none rounded-2xl text-base font-medium focus:ring-2 focus:ring-blue-500 transition-all'
            }),
            'target_role': forms.TextInput(attrs={
                'class': 'w-full px-5 py-4 bg-gray-50 border-none rounded-2xl text-base font-medium focus:ring-2 focus:ring-blue-500 transition-all',
                'placeholder': 'e.g. ALL, MANAGER, etc.'
            }),
            'scheduled_at': forms.DateTimeInput(attrs={
                'class': 'w-full px-5 py-4 bg-gray-50 border-none rounded-2xl text-base font-medium focus:ring-2 focus:ring-blue-500 transition-all',
                'type': 'datetime-local'
            }),
            'expires_at': forms.DateTimeInput(attrs={
                'class': 'w-full px-5 py-4 bg-gray-50 border-none rounded-2xl text-base font-medium focus:ring-2 focus:ring-blue-500 transition-all',
                'type': 'datetime-local'
            }),
            'require_acknowledgement': forms.CheckboxInput(attrs={
                'class': 'sr-only peer'
            }),
            'is_pinned': forms.CheckboxInput(attrs={
                'class': 'sr-only peer'
            }),
        }

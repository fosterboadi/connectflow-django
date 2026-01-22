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
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Announcement Title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Announcement Content'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'target_department': forms.Select(attrs={'class': 'form-control'}),
            'target_team': forms.Select(attrs={'class': 'form-control'}),
            'target_role': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MANAGER'}),
            'scheduled_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'expires_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'require_acknowledgement': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
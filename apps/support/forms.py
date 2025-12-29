from django import forms
from django.db.models import Q
from .models import Ticket, TicketMessage

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['subject', 'category', 'priority'] # Priority can be suggested by user, but system may override
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition font-bold text-gray-800 placeholder-gray-400',
                'placeholder': 'Briefly describe your issue...'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition font-bold text-gray-800'
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition font-bold text-gray-800'
            }),
        }

class TicketMessageForm(forms.ModelForm):
    class Meta:
        model = TicketMessage
        fields = ['content', 'attachment']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition font-medium text-gray-800 placeholder-gray-400',
                'rows': 3,
                'placeholder': 'Type your reply here...'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-black file:uppercase file:tracking-widest file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'
            })
        }

class TicketAdminForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['status', 'priority', 'assigned_to']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition font-bold text-gray-800'
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition font-bold text-gray-800'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition font-bold text-gray-800'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.accounts.models import User
        # Only allow assigning to staff or super admins
        self.fields['assigned_to'].queryset = User.objects.filter(
            Q(is_staff=True) | Q(role=User.Role.SUPER_ADMIN)
        )

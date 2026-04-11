from rest_framework import serializers
from .models import Form, FormField, FormResponse
from apps.accounts.serializers import UserSerializer

class FormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormField
        fields = [
            'id', 'label', 'field_type', 'is_required', 'placeholder', 
            'help_text', 'options', 'min_value', 'max_value', 
            'max_length', 'pattern', 'show_if_field', 'show_if_value', 'order'
        ]

class FormSerializer(serializers.ModelSerializer):
    fields = FormFieldSerializer(many=True, read_only=True)
    creator_details = UserSerializer(source='created_by', read_only=True)
    response_count = serializers.ReadOnlyField()

    class Meta:
        model = Form
        fields = [
            'id', 'organization', 'title', 'description', 'form_type', 
            'share_link', 'is_public', 'allow_anonymous', 'require_login', 
            'is_active', 'accepts_responses', 'max_responses', 'closes_at', 
            'send_email_on_submit', 'notification_emails', 'created_by', 
            'creator_details', 'fields', 'response_count', 'created_at'
        ]
        read_only_fields = ['share_link', 'created_at']

class FormResponseSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    respondent_name = serializers.ReadOnlyField()

    class Meta:
        model = FormResponse
        fields = [
            'id', 'form', 'user', 'user_details', 'is_anonymous', 
            'respondent_email', 'answers', 'submitted_at', 'respondent_name'
        ]
        read_only_fields = ['submitted_at']

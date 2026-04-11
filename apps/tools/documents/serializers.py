from rest_framework import serializers
from .models import Folder, Document, DocumentVersion
from apps.accounts.serializers import UserSerializer

class FolderSerializer(serializers.ModelSerializer):
    created_by_details = UserSerializer(source='created_by', read_only=True)
    full_path = serializers.ReadOnlyField()

    class Meta:
        model = Folder
        fields = [
            'id', 'organization', 'parent', 'name', 'description', 
            'created_by', 'created_by_details', 'full_path', 
            'created_at', 'updated_at'
        ]

class DocumentVersionSerializer(serializers.ModelSerializer):
    created_by_details = UserSerializer(source='created_by', read_only=True)
    file_url = serializers.FileField(source='file', read_only=True)

    class Meta:
        model = DocumentVersion
        fields = [
            'id', 'document', 'version_number', 'file_url', 
            'file_name', 'file_size', 'file_type', 'change_log', 
            'created_by', 'created_by_details', 'created_at'
        ]

class DocumentSerializer(serializers.ModelSerializer):
    created_by_details = UserSerializer(source='created_by', read_only=True)
    latest_version = DocumentVersionSerializer(read_only=True)
    folder_name = serializers.ReadOnlyField(source='folder.name')

    class Meta:
        model = Document
        fields = [
            'id', 'organization', 'folder', 'folder_name', 'title', 
            'description', 'is_public', 'created_by', 'created_by_details', 
            'latest_version', 'created_at', 'updated_at'
        ]

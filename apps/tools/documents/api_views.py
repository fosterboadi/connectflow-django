from rest_framework import viewsets, permissions, filters
from .models import Folder, Document, DocumentVersion
from .serializers import FolderSerializer, DocumentSerializer, DocumentVersionSerializer

class FolderViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(organization=self.request.user.organization)

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            organization=self.request.user.organization
        )

    def perform_update(self, serializer):
        if serializer.instance.created_by_id != self.request.user.id and not self.request.user.is_admin:
            raise permissions.PermissionDenied(
                'Only the folder creator or an administrator can edit this folder.'
            )
        serializer.save()

    def perform_destroy(self, instance):
        if instance.created_by_id != self.request.user.id and not self.request.user.is_admin:
            raise permissions.PermissionDenied(
                'Only the folder creator or an administrator can delete this folder.'
            )
        instance.delete()

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']

    def get_queryset(self):
        return self.queryset.filter(organization=self.request.user.organization)

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            organization=self.request.user.organization
        )

    def perform_update(self, serializer):
        if serializer.instance.created_by_id != self.request.user.id and not self.request.user.is_admin:
            raise permissions.PermissionDenied(
                'Only the document creator or an administrator can edit this document.'
            )
        serializer.save()

    def perform_destroy(self, instance):
        if instance.created_by_id != self.request.user.id and not self.request.user.is_admin:
            raise permissions.PermissionDenied(
                'Only the document creator or an administrator can delete this document.'
            )
        instance.delete()

class DocumentVersionViewSet(viewsets.ModelViewSet):
    queryset = DocumentVersion.objects.all()
    serializer_class = DocumentVersionSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'head', 'options']

    def get_queryset(self):
        return self.queryset.filter(document__organization=self.request.user.organization)

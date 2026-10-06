from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from .models import Form, FormField, FormResponse
from .serializers import FormSerializer, FormFieldSerializer, FormResponseSerializer

class FormViewSet(viewsets.ModelViewSet):
    queryset = Form.objects.all()
    serializer_class = FormSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']

    def get_queryset(self):
        return self.queryset.filter(organization=self.request.user.organization)

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            organization=self.request.user.organization
        )

    def perform_update(self, serializer):
        if serializer.instance.created_by_id != self.request.user.id and not self.request.user.is_superuser:
            raise permissions.PermissionDenied('Only the form creator can edit this form.')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.created_by_id != self.request.user.id and not self.request.user.is_superuser:
            raise permissions.PermissionDenied('Only the form creator can delete this form.')
        instance.delete()

class FormFieldViewSet(viewsets.ModelViewSet):
    queryset = FormField.objects.all()
    serializer_class = FormFieldSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(form__organization=self.request.user.organization)

    def perform_create(self, serializer):
        form = serializer.validated_data['form']
        if form.organization_id != self.request.user.organization_id:
            raise permissions.PermissionDenied('This form is outside your organization.')
        serializer.save()

    def _check_form_owner(self, instance):
        if instance.form.created_by_id != self.request.user.id and not self.request.user.is_superuser:
            raise permissions.PermissionDenied('Only the form creator can manage its fields.')

    def perform_update(self, serializer):
        self._check_form_owner(serializer.instance)
        serializer.save()

    def perform_destroy(self, instance):
        self._check_form_owner(instance)
        instance.delete()

class FormResponseViewSet(viewsets.ModelViewSet):
    queryset = FormResponse.objects.all()
    serializer_class = FormResponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'head', 'options']

    def get_queryset(self):
        # Owners can see all responses, users can see their own
        if self.request.user.role in ['SUPER_ADMIN', 'DEPT_HEAD']:
            return self.queryset.filter(form__organization=self.request.user.organization)
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            is_anonymous=False,
        )

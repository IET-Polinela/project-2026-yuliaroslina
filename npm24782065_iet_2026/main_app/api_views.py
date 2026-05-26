from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from .models import Report
from .permissions import IsOwnerAndDraftOrReadOnly
from .serializers import ReportSerializer


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_admin:
            return Report.objects.exclude(status='DRAFT')

        return (
            Report.objects.exclude(status='DRAFT')
            | Report.objects.filter(status='DRAFT', reporter=user)
        ).distinct()

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [
                permissions.IsAuthenticated(),
                IsOwnerAndDraftOrReadOnly()
            ]

        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        if not self.request.user.is_member:
            raise PermissionDenied(
                'Hanya Citizen yang boleh membuat report.'
            )

        serializer.save(reporter=self.request.user)

    def perform_update(self, serializer):
        user = self.request.user

        if user.is_admin:
            serializer.save()
        else:
            serializer.save(reporter=user)
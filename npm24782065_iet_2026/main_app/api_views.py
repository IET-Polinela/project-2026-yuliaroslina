from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination

from .models import Report
from .permissions import IsOwnerAndDraftOrReadOnly
from .serializers import ReportSerializer


class ReportPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    pagination_class = ReportPagination

    def get_queryset(self):
        user = self.request.user
        tab = self.request.query_params.get('tab')

        queryset = Report.objects.all().order_by('-updated_at')

        if tab == 'my_reports':
            return queryset.filter(reporter=user)

        if tab == 'feed':
            return queryset.exclude(reporter=user).exclude(status='DRAFT')

        if user.is_admin:
            return queryset.exclude(status='DRAFT')

        return (
            queryset.exclude(status='DRAFT')
            | queryset.filter(status='DRAFT', reporter=user)
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
from django.urls import path

from .views import (
    HomeView,
    ReportListView,
    ReportDetailView,
    ReportCreateView,
    ReportUpdateView,
    ReportDeleteView,
    ReportUpdateStatusView,
    report_search_api,
    report_detail_api,
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),

    path('reports/', ReportListView.as_view(), name='report_list'),

    path('reports/search/', report_search_api, name='report_search'),
    path('reports/search/', report_search_api, name='report_search_api'),

    path('add/', ReportCreateView.as_view(), name='add_report'),

    path('report/<int:pk>/api/', report_detail_api, name='report_detail_api'),
    path('report/<int:pk>/', ReportDetailView.as_view(), name='report_detail'),

    path('update/<int:pk>/', ReportUpdateView.as_view(), name='update_report'),
    path('delete/<int:pk>/', ReportDeleteView.as_view(), name='delete_report'),

    path('update-status/<int:pk>/', ReportUpdateStatusView.as_view(), name='update_status'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('add/', views.add_report, name='add_report'),
    path('update/<int:id>/', views.update_report, name='update_report'),
    path('delete/<int:id>/', views.delete_report, name='delete_report'),
]
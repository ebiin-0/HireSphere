from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    path('user/<int:user_id>/toggle-verify/', views.toggle_user_verification, name='toggle_user_verify'),
    path('company/<int:company_id>/toggle-verify/', views.toggle_company_verification, name='toggle_company_verify'),
    path('job/<int:job_id>/toggle-status/', views.toggle_job_status, name='toggle_job_status'),
]

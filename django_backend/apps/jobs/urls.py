from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.home, name='home'),
    path('list/', views.job_list, name='job_list'),
    path('<int:pk>/', views.job_detail, name='job_detail'),
    path('create/', views.create_job, name='create_job'),
    path('<int:pk>/edit/', views.edit_job, name='edit_job'),
    path('<int:pk>/apply/', views.apply_job, name='apply_job'),
    path('<int:pk>/applicants/', views.manage_applicants, name='manage_applicants'),
    path('application/<int:pk>/status/', views.update_application_status, name='update_application_status'),
    path('api/list/', views.api_jobs_list, name='api_jobs_list'),
]

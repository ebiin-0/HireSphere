from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    path('', views.company_list, name='list'),
    path('directory/', views.company_list, name='directory'),
    path('dashboard/', views.company_dashboard, name='dashboard'),
    path('create/', views.create_company, name='create'),
    path('edit/', views.edit_company, name='edit'),
    path('<int:pk>/', views.company_detail, name='detail'),
]

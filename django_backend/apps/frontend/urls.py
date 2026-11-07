from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    path('<slug:slug>.html', views.page, name='slug_page'),
]

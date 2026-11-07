from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.jobs import views as job_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('users/', include('apps.users.urls')),
    path('companies/', include('apps.companies.urls')),
    path('jobs/', include('apps.jobs.urls')),
    path('admin-panel/', include('apps.admin_panel.urls')),
    path('', job_views.home, name='root_home'),
    path('', include('apps.frontend.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

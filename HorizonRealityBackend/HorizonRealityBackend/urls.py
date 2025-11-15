"""
URL configuration for HorizonRealityBackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from services import views as services_views
admin.site.site_header = "Admin Dashboard"
admin.site.site_title = "Horizon Reality Admin Portal"
admin.site.index_title = "Horizon Reality Admin Portal"


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('home.urls')),
    path('', include('users.urls')),
    path('favorite/<int:property_id>/', services_views.toggle_favorite, name='toggle_favorite'),
    path('favorite-status/<int:property_id>/', services_views.get_favorite_status, name='get_favorite_status'),
    path('my-favorites/', services_views.my_favorites, name='my_favorites'),
    path('properties/', services_views.property_list_view, name='property_list'),
    path('property-calc/', services_views.property_calculator_view, name='property_calc'),
    path('property/', include(('services.urls', 'property'), namespace='property')),
    path('blogs/', include(('blogs.urls', 'blogs'), namespace='blogs')),
    path('chatbot/', include('chatbot.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
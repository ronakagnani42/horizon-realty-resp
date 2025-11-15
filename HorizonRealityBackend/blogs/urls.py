from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .views import *

app_name = 'blogs'

urlpatterns = [
    path('', views.blogs_view, name='blog_list'),
    path('<slug:slug>/', views.blog_detail, name='blog_detail'),
]
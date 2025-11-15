from django.urls import path
from . import views

app_name = 'property'

urlpatterns = [    
    path('', views.property_list_view, name='property_home'),
    path('<slug:slug>/', views.property_detail_view, name='property_detail'),
    path('<slug:slug>/inquiry/', views.property_inquiry, name='property_inquiry'),
]
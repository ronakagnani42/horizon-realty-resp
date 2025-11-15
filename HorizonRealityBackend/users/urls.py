from django.urls import path
from .views import *
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('contact-us/', views.contact_us_view, name='contact-us'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/update/', views.update_profile_view, name='update_profile'),
    path('profile/data/', views.get_user_data_json, name='user_data_json'),
]
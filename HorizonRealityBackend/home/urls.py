from django.urls import path
from .views import *
from .forms import CustomPasswordResetForm
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
     path('', views.index_view, name='home'),
    
     path('about-us/', views.about_us_view, name='about-us'),
     path('team-members/', views.our_team_member_view, name='team-members'),
     path('service/', views.services, name='service'),
     path('services/', views.service_form, name='services'),
     path('service/<slug:slug>/', views.service_detail, name='service_detail'),  
     path('terms-of-services/', views.terms_of_services, name='terms-of-services'),
     path('terms-of-interior-services/', views.terms_of_interior_services, name='terms-of-interior-services'),

    # Other URL patterns
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='home/password_reset.html',
        email_template_name='home/password_reset_email.html',
        html_email_template_name='home/password_reset_email.html',
        subject_template_name='home/password_reset_subject.txt', 
        success_url='/password-reset/done/'
    ), name='password_reset'),

    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='home/password_reset_done.html'
    ), name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='home/password_reset_confirm.html',
        form_class=CustomPasswordResetForm,
        success_url='/password-reset-complete/'
    ), name='password_reset_confirm'),

    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='home/password_reset_complete.html'
    ), name='password_reset_complete'),
    path('interior-design/', views.interior_design_form_view, name='interior_design_form'),
    path('residential-property/', views.sell_properties_view, name='residential_property'),
    path('commercial-property/', views.sell_commercial_properties_view, name='commercial_property'),
    path('buy-residential-property/', views.buy_residential_property, name='buy_residential_property'),
    path('property-search-results/', views.property_search_results, name='property_search_results'),
    path('commercial-property-search-results/', views.commercial_property_search_results, name='commercial_property_search_results'),
    path('buy-commercial-property/', views.buy_commercial_property, name='buy_commercial_property'),




]
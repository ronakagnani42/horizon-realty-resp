from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, QueryDict
from .models import Statistics, TeamMember, Testimonial, AboutUs, Service
from services.models import BuyProperties
from .forms import UserRegistrationForm, LoginForm, SellResidentialPropertyForm, SellCommercialPropertyForm,BuyPropertySearchForm, BuyCommercialPropertySearchForm
from django.contrib.auth import login, authenticate, logout
from django.db.models import Q
from users.models import CustomUser
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import logging
from itertools import chain
from operator import attrgetter
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from services.forms import *
'''
This module contains views for handling various pages and functionalities on the website.
Each view corresponds to a different page or feature in the frontend, such as displaying services,
handling contact form submissions, and managing user authentication.

Views:
------

1. index_view:
   - Handles the home page view.
   - On GET: Displays statistics, testimonials, and services.
   - On POST: Processes the contact form submission, saves data, and provides feedback to the user.

2. register:
   - Handles user registration.
   - On GET: Displays the registration form.
   - On POST: Validates the form, creates a new user, logs them in, and redirects them to the homepage.

3. login_view:
   - Handles user login.
   - On GET: Displays the login form.
   - On POST: Authenticates the user's credentials and logs them in if valid.

4. about_us_view:
   - Displays the "About Us" page.
   - Retrieves the AboutUs instance and converts YouTube URLs to embeddable formats for video display.

5. contact_us_view:
   - Displays and processes the "Contact Us" form.
   - On GET: Shows the contact form.
   - On POST: Saves the contact submission and provides feedback to the user.

6. our_team_member_view:
   - Renders the "Our Team" page displaying a list of team members.

7. logout_view:
   - Logs out the current user and redirects them to the homepage.

8. service_detail:
   - Displays the details of a specific service based on its slug.

9. terms_of_services:
   - Renders the "Terms of Service" page.

10. services:
    - Displays the list of available services on the homepage.

Each view handles GET and POST requests where necessary and interacts with the corresponding model or form to retrieve and store data.
'''

def index_view(request):
    '''
    Home page view.
    - On GET: Fetches statistics, testimonials, services, and properties to display.
    - On POST: Handles contact form submission, saves data to the database,
      and returns a success or error message.
    '''
    testimonials = Testimonial.objects.filter(is_testimonial_active=True)
    project_statistics = Statistics.objects.all()
    services = Service.objects.filter(is_service_active=True)
    leasing_properties = BuyProperties.objects.filter(
        category__iexact='leasing'
    ).order_by('-id')
    investment_properties = BuyProperties.objects.filter(
        category='investment'
    ).order_by('-id')
    resale_properties = BuyProperties.objects.filter(
        category='resale_residential'
    ).order_by('-id')
    all_property_ids = list(leasing_properties.values_list('id', flat=True)) + \
                      list(investment_properties.values_list('id', flat=True)) + \
                      list(resale_properties.values_list('id', flat=True))
    all_property_ids = list(set(all_property_ids))
    all_properties = BuyProperties.objects.filter(id__in=all_property_ids).order_by('-id')
    available_categories = list(BuyProperties.objects.values_list('category', flat=True).distinct())
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        try:
            contact_submission = ContactSubmission(
                name=name, email=email, subject=subject, message=message
            )
            contact_submission.save()
            messages.success(request, "Your message has been sent. Thank you!")
            return redirect('home')
        except Exception as e:
            messages.error(request, "There was an error sending your message. Please try again.")
            return redirect('home')
    context = {
        'statistics': project_statistics,
        'testimonials': testimonials,
        'services': services,
        'all_properties': all_properties,
        'leasing_properties': leasing_properties,
        'investment_properties': investment_properties,
        'resale_properties': resale_properties
    }
    return render(request, 'home/index.html', context)

def about_us_view(request):
    '''
    Displays the "About Us" page.
    - Retrieves the AboutUs model instance if it exists.
    - Converts YouTube links to embed format if present.
    '''
    about = AboutUs.objects.first()
    embed_url = None
    if about and about.introduction_video:
        url = about.introduction_video.strip()
        if "watch?v=" in url:
            embed_url = url.replace("watch?v=", "embed/")
        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[1]
            embed_url = f"https://www.youtube.com/embed/{video_id}"
        else:
            embed_url = url
    return render(request, 'home/about_us.html', {
        'about': about,
        'embed_video_url': embed_url,
    })

def our_team_member_view(request):
    '''
    Renders a list of team members on the "Our Team" page.
    '''
    team_member = TeamMember.objects.all()
    return render(request, 'home/our_team_members.html', {'team_members': team_member})

def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug)
    service_images = service.images.all().order_by('order')
    if not service_images.exists() and service.icon:
        fallback_image = service.icon
    else:
        fallback_image = None
    context = {
        'service': service,
        'service_images': service_images,
        'fallback_image': fallback_image
    }
    return render(request, 'home/service_detail.html', context)

def terms_of_services(request):
    return render(request, 'home/terms_of_services.html')

def terms_of_interior_services(request):
    return render(request, 'home/terms_of_interior_services.html')

def services(request):
    return render(request, 'index.html')

def service_form(request):
    return render(request, 'home/service_form.html')

def interior_design_form_view(request):
    """View to handle interior design request form"""
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                form = InteriorDesignRequestForm(request.POST)
                if form.is_valid():
                    form_instance = form.save()
                    return JsonResponse({
                        'success': True,
                        'message': 'Your interior design request has been submitted successfully!',
                        'redirect_url': None
                    })
                else:
                    errors = {}
                    for field, error_list in form.errors.items():
                        errors[field] = [str(error) for error in error_list]  
                    return JsonResponse({
                        'success': False,
                        'message': 'Please correct the errors below.',
                        'errors': errors
                    })     
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'An error occurred: {str(e)}'
                })
        else:
            form = InteriorDesignRequestForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your interior design request has been submitted successfully!')
                return redirect('interior_design_form')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
    else:
        form = InteriorDesignRequestForm()
    check_our_work_brochures = CheckOurWorkBrochure.objects.filter(is_active=True)
    context = {
        'form': form,
        'property_choices': InteriorDesignRequest.PROPERTY_TYPE_CHOICES,
        'service_choices': InteriorDesignRequest.SERVICE_TYPE_CHOICES,
        'check_our_work_brochures': check_our_work_brochures,
    }
    return render(request, 'home/interior_design.html', context)

def sell_properties_view(request):
    """View to handle property selling form"""
    if request.method == 'POST':
        form = SellResidentialPropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_instance = form.save(commit=False)
            statuses = []
            if form.cleaned_data.get('is_for_new'):
                statuses.append('new')
            if form.cleaned_data.get('is_for_resale'):
                statuses.append('resale')
            if form.cleaned_data.get('is_for_rent'):
                statuses.append('rent')
            if form.cleaned_data.get('is_for_lease'):
                statuses.append('lease')
            property_instance.status = statuses[0] if statuses else 'new'
            property_instance.save()
            contact_info = {
                'name': form.cleaned_data.get('contact_name'),
                'phone': form.cleaned_data.get('contact_phone'),
                'email': form.cleaned_data.get('contact_email'),
                'property_id': property_instance.id
            }
            messages.success(request, 'Property submitted successfully!')
            return redirect('residential_property')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SellResidentialPropertyForm()
    locations = PropertyLocation.objects.all()
    context = {
        'form': form,
        'locations': locations,
        'residential_choices': SellResidentialProperties.RESIDENTIAL_CONFIG_CHOICES,
    }
    return render(request, 'home/sell_res_property.html', context)

def sell_commercial_properties_view(request):
    """View to handle property selling form"""
    if request.method == 'POST':
        form = SellCommercialPropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_instance = form.save(commit=False)
            statuses = []
            if form.cleaned_data.get('is_for_new'):
                statuses.append('new')
            if form.cleaned_data.get('is_for_resale'):
                statuses.append('resale')
            if form.cleaned_data.get('is_for_rent'):
                statuses.append('rent')
            if form.cleaned_data.get('is_for_lease'):
                statuses.append('lease')
            property_instance.status = statuses[0] if statuses else 'new'
            property_instance.save()
            contact_info = {
                'name': form.cleaned_data.get('contact_name'),
                'phone': form.cleaned_data.get('contact_phone'),
                'email': form.cleaned_data.get('contact_email'),
                'property_id': property_instance.id
            }
            messages.success(request, 'Property submitted successfully!')
            return redirect('commercial_property')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SellCommercialPropertyForm()
    locations = PropertyLocation.objects.all()
    context = {
        'form': form,
        'locations': locations,
        'commercial_choices': SellCommercialProperties.COMMERCIAL_TYPE_CHOICES,
        'furnishing_choices': SellCommercialProperties.FURNISHING_CHOICES,
    }
    return render(request, 'home/sell_comm_property.html', context)

def get_property_configurations(request):
    """AJAX view to get configurations based on property type"""
    property_type = request.GET.get('property_type')
    if property_type == 'residential':
        configurations = SellResidentialProperties.RESIDENTIAL_CONFIG_CHOICES
    elif property_type == 'commercial':
        configurations = SellCommercialProperties.COMMERCIAL_TYPE_CHOICES
    else:
        configurations = []
    return JsonResponse({'configurations': configurations})

def buy_residential_property(request):
    status_choices = BuyProperties.STATUS_CHOICES
    configuration_choices = BuyProperties.RESIDENTIAL_CONFIG_CHOICES
    locations = PropertyLocation.objects.all()
    form = BuyPropertySearchForm(request.GET or None)
    if request.method == 'GET' and form.is_valid() and any(request.GET.values()):
        query_params = request.GET.copy()
        return redirect(reverse('property_search_results') + '?' + query_params.urlencode())
    context = {
        'form': form,
        'status_choices': status_choices,
        'configuration_choices': configuration_choices,
        'locations': locations,
    }
    return render(request, 'home/buy_residential_property.html', context)

def property_search_results(request):
    """View to handle property search results with debugging - includes approved sell properties"""    
    form = BuyPropertySearchForm(request.GET or None)
    properties = []
    total_properties = 0
    buy_properties_queryset = BuyProperties.objects.filter(property_type='residential')
    sell_properties_queryset = SellResidentialProperties.objects.filter(is_approved=True)
    initial_buy_count = buy_properties_queryset.count()
    initial_sell_count = sell_properties_queryset.count()
    status_values = request.GET.getlist('status')
    if status_values:
        buy_properties_queryset = buy_properties_queryset.filter(status__in=status_values)
        sell_properties_queryset = sell_properties_queryset.filter(status__in=status_values)
        existing_buy_statuses = BuyProperties.objects.values_list('status', flat=True).distinct()
        existing_sell_statuses = SellResidentialProperties.objects.values_list('status', flat=True).distinct()
    config_values = request.GET.getlist('configuration')
    if config_values:
        buy_properties_queryset = buy_properties_queryset.filter(configuration__in=config_values)
        sell_properties_queryset = sell_properties_queryset.filter(configuration__in=config_values)
        existing_buy_configs = BuyProperties.objects.values_list('configuration', flat=True).distinct()
        existing_sell_configs = SellResidentialProperties.objects.values_list('configuration', flat=True).distinct()
    location_values = request.GET.getlist('locations')
    if location_values:
        try:
            location_ids = [int(loc_id) for loc_id in location_values if loc_id.isdigit()]
            buy_properties_queryset = buy_properties_queryset.filter(locations__id__in=location_ids)
            sell_properties_queryset = sell_properties_queryset.filter(locations__id__in=location_ids)
        except ValueError as e:
            print(f"Error converting location IDs: {e}")
    area_value = request.GET.get('area_range')
    if area_value:
        try:
            area_value = int(area_value)
            buy_properties_queryset = buy_properties_queryset.filter(area__lte=area_value)
            sell_properties_queryset = sell_properties_queryset.filter(area__lte=area_value)
        except ValueError:
            print("Invalid area value")
    budget_value = request.GET.get('budget_range')
    if budget_value:
        try:
            budget_value = int(budget_value)
            buy_properties_queryset = buy_properties_queryset.filter(min_budget__lte=budget_value)
            sell_properties_queryset = sell_properties_queryset.filter(budget__lte=budget_value)
        except ValueError:
            print("Invalid budget value")
    buy_properties = buy_properties_queryset.distinct()
    sell_properties = sell_properties_queryset.distinct()
    for prop in buy_properties:
        prop.property_source = 'buy'
        prop.is_sell_property = False
    for prop in sell_properties:
        prop.property_source = 'sell'
        prop.is_sell_property = True
        prop.min_budget = prop.budget
        prop.max_budget = prop.budget
        prop.min_budget_unit = 'rupees'
        prop.max_budget_unit = 'rupees'
        prop.salient_features = prop.additional_details or ''
    properties = list(chain(buy_properties, sell_properties))
    total_properties = len(properties)
    if properties:
        for prop in properties[:3]:
            source = "Buy" if not prop.is_sell_property else "Sell"
    context = {
        'form': form,
        'properties': properties,
        'total_properties': total_properties,
        'search_performed': True,
        'debug_info': {
            'status_values': status_values,
            'config_values': config_values,
            'location_values': location_values,
            'area_value': area_value,
            'budget_value': budget_value,
            'buy_count': buy_properties.count(),
            'sell_count': sell_properties.count(),
        }
    }
    return render(request, 'home/property_search_results.html', context)

def buy_commercial_property(request):
    status_choices = BuyProperties.STATUS_CHOICES
    configuration_choices = BuyProperties.COMMERCIAL_TYPE_CHOICES
    locations = PropertyLocation.objects.all()
    form = BuyCommercialPropertySearchForm(request.GET or None)
    context = {
        'form': form,
        'status_choices': status_choices,
        'configuration_choices': configuration_choices,
        'locations': locations,
    }
    return render(request, 'home/buy_commercial_property.html', context)

def commercial_property_search_results(request):
    """View to handle property search results with debugging - includes approved sell properties"""
    form = BuyCommercialPropertySearchForm(request.GET or None)
    properties = []
    total_properties = 0
    buy_properties_queryset = BuyProperties.objects.filter(property_type='commercial')
    sell_properties_queryset = SellCommercialProperties.objects.filter(
        is_approved=True)
    initial_buy_count = buy_properties_queryset.count()
    initial_sell_count = sell_properties_queryset.count()
    status_values = request.GET.getlist('status')
    if status_values:
        buy_properties_queryset = buy_properties_queryset.filter(status__in=status_values)
        sell_properties_queryset = sell_properties_queryset.filter(status__in=status_values)
        existing_buy_statuses = BuyProperties.objects.filter(property_type='commercial').values_list('status', flat=True).distinct()
        existing_sell_statuses = SellCommercialProperties.objects.values_list('status', flat=True).distinct()
    commercial_type_values = request.GET.getlist('commercial_type')
    if commercial_type_values:
        buy_properties_queryset = buy_properties_queryset.filter(commercial_type__in=commercial_type_values)
        sell_properties_queryset = sell_properties_queryset.filter(commercial_type__in=commercial_type_values)
        existing_buy_commercial_type = BuyProperties.objects.filter(property_type='commercial').values_list('commercial_type', flat=True).distinct()
        existing_sell_commercial_type = SellCommercialProperties.objects.filter(property_type='commercial').values_list('commercial_type', flat=True).distinct()
    furnishing_values = request.GET.getlist('furnishing')
    if furnishing_values:
        buy_properties_queryset = buy_properties_queryset.filter(furnishing__in=furnishing_values)
        sell_properties_queryset = sell_properties_queryset.filter(furnishing__in=furnishing_values)
        existing_buy_furnishing_values = BuyProperties.objects.filter(property_type='commercial').values_list('furnishing', flat=True).distinct()
        existing_sell_furnishing_values = SellCommercialProperties.objects.values_list('furnishing', flat=True).distinct()
    location_values = request.GET.getlist('locations')
    if location_values:
        try:
            location_ids = [int(loc_id) for loc_id in location_values if loc_id.isdigit()]
            buy_properties_queryset = buy_properties_queryset.filter(locations__id__in=location_ids)
            sell_properties_queryset = sell_properties_queryset.filter(locations__id__in=location_ids)
        except ValueError as e:
            print(f"Error converting location IDs: {e}")
    area_value = request.GET.get('area_range')
    if area_value:
        try:
            area_value = int(area_value)
            buy_properties_queryset = buy_properties_queryset.filter(area__lte=area_value)
            sell_properties_queryset = sell_properties_queryset.filter(area__lte=area_value)
        except ValueError:
            print("Invalid area value")
    budget_value = request.GET.get('budget_range')
    if budget_value:
        try:
            budget_value = int(budget_value)
            buy_properties_queryset = buy_properties_queryset.filter(min_budget__lte=budget_value)
            sell_properties_queryset = sell_properties_queryset.filter(budget__lte=budget_value)
        except ValueError:
            print("Invalid budget value")
    buy_properties = buy_properties_queryset.distinct()
    sell_properties = sell_properties_queryset.distinct()
    for prop in buy_properties:
        prop.property_source = 'buy'
        prop.is_sell_property = False
    for prop in sell_properties:
        prop.property_source = 'sell'
        prop.is_sell_property = True
        prop.min_budget = prop.budget
        prop.max_budget = prop.budget
        prop.min_budget_unit = 'rupees' 
        prop.max_budget_unit = 'rupees'
        prop.salient_features = prop.additional_details or ''
    properties = list(chain(buy_properties, sell_properties))
    total_properties = len(properties)
    if properties:
        for prop in properties[:3]:
            source = "Buy" if not prop.is_sell_property else "Sell"
    context = {
        'form': form,
        'properties': properties,
        'total_properties': total_properties,
        'search_performed': True,
        'debug_info': {
            'furnishing_values': furnishing_values,
            'status_values': status_values,
            'commercial_type_values': commercial_type_values,
            'location_values': location_values,
            'area_value': area_value,
            'budget_value': budget_value,
            'buy_count': buy_properties.count(),
            'sell_count': sell_properties.count(),
        }
    }
    return render(request, 'home/commercial_property_search_results.html', context)
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from . models import BuyProperties, PropertyInquiry,PropertyLocation, UserFavorite,InteriorDesignRequest,UserFavorite
from users.models import ContactInformation
from django.views.decorators.csrf import ensure_csrf_cookie
from .forms import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
import re
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
def property_detail_view(request, slug):
    """
    Detail view for a specific property.
    
    Displays all details about a particular property including
    its location, configuration, area, budget, etc.
    """
    try:
        property = get_object_or_404(BuyProperties, slug=slug)
    except BuyProperties.DoesNotExist:
        messages.error(request, "Property not found.")
        return redirect('home')
    related_properties = BuyProperties.objects.filter(
        property_type=property.property_type,
        locations=property.locations
    ).exclude(slug=slug)
    property_images = property.images.all()
    property_videos = property.videos.all()
    nearby_places = property.nearby_amenities.all()
    feature_amenities = property.feature_amenities.all()
    try:
        contact_info = ContactInformation.objects.filter(is_main_office=True).first()
    except:
        contact_info = None
    context = {
        'property': property,
        'related_properties': related_properties,
        'property_images': property_images,
        'property_videos': property_videos,
        'nearby_places': nearby_places,
        'feature_amenities': feature_amenities,
        'contact_info': contact_info
    }
    return render(request, 'services/property_detail.html', context)

@ensure_csrf_cookie
def property_inquiry(request, slug):
    if request.method == 'POST':
        property = get_object_or_404(BuyProperties, slug=slug)
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message', '')
        inquiry = PropertyInquiry.objects.create(
            property=property,
            name=name,
            email=email,
            phone=phone,
            message=message
        )
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('property_detail', slug=slug)
    return redirect('property_detail', slug=slug)

def property_list_view(request):
    properties = BuyProperties.objects.filter(is_property_active=True)
    property_type = request.GET.get('property_type')
    category = request.GET.get('category')
    configuration = request.GET.get('configuration')
    location = request.GET.get('location')
    status = request.GET.get('status')
    min_budget = request.GET.get('min_budget')
    max_budget = request.GET.get('max_budget')
    search_query = request.GET.get('search', '').strip()
    if search_query:
        properties = properties.filter(
            Q(project_name__icontains=search_query) |
            Q(configuration__icontains=search_query) |
            Q(locations__name__icontains=search_query)
        ).distinct()
    if property_type:
        properties = properties.filter(property_type=property_type)
    if category and category != 'all':
        properties = properties.filter(category=category)
    if configuration:
        properties = properties.filter(configuration=configuration)
    if location:
        properties = properties.filter(locations=location)
    if status:
        properties = properties.filter(status=status)
    if min_budget:
        properties = properties.filter(
            Q(min_budget__gte=min_budget, min_budget_unit='lakhs') |
            Q(min_budget__gte=min_budget/100, min_budget_unit='crores')
        )
    if max_budget:
        properties = properties.filter(
            Q(max_budget__lte=max_budget, max_budget_unit='lakhs') |
            Q(max_budget__lte=max_budget/100, max_budget_unit='crores')
        )
    properties = properties.order_by('id')
    paginator = Paginator(properties, 6)
    page_number = request.GET.get('page')
    try:
        paginated_properties = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_properties = paginator.page(1)
    except EmptyPage:
        paginated_properties = paginator.page(paginator.num_pages)
    locations = PropertyLocation.objects.all()
    context = {
        'properties': paginated_properties,
        'locations': locations,
        'property_types': BuyProperties.PROPERTY_TYPE_CHOICES,
        'categories': BuyProperties.PROPERTY_CATEGORY_CHOICES,
        'residential_configurations': BuyProperties.RESIDENTIAL_CONFIG_CHOICES,
        'commercial_configurations': BuyProperties.COMMERCIAL_TYPE_CHOICES,
        'statuses': BuyProperties.STATUS_CHOICES,
        'current_filters': {
            'property_type': property_type,
            'category': category,
            'configuration': configuration,
            'location': location,
            'status': status,
            'min_budget': min_budget,
            'max_budget': max_budget,
            'search': search_query,
        },
        'total_properties': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': paginated_properties.number,
        'has_previous': paginated_properties.has_previous(),
        'has_next': paginated_properties.has_next(),
        'page_range': paginator.page_range,
    }
    return render(request, 'services/property_list.html', context)

def property_calculator_view(request):
    if request.method == 'POST':
        form = PropertyCalculatorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your property information has been submitted successfully. Our team will contact you shortly with the valuation.')
            return redirect('property_calc')
        else:
            messages.error(request, 'There was an error with your submission. Please check the form and try again.')
    else:
        form = PropertyCalculatorForm()
    return render(request, 'services/property_calculator.html', {'form': form})

@login_required
@require_POST
def toggle_favorite(request, property_id):
    """Toggle a property as favorite for the current user."""
    property_obj = get_object_or_404(BuyProperties, id=property_id)
    user = request.user
    try:
        favorite = UserFavorite.objects.filter(user=user, property=property_obj).first()
        if favorite:
            favorite.delete()
            is_favorite = False
            message = "Removed from favorites"
        else:
            UserFavorite.objects.create(user=user, property=property_obj)
            is_favorite = True
            message = "Added to favorites"
        response_data = {
            'success': True,
            'is_favorite': is_favorite,
            'property_id': property_id,
            'message': message
        }
        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
def my_favorites(request):
    """Display user's favorite properties."""
    favorites = UserFavorite.objects.filter(user=request.user).select_related('property')
    favorite_properties = [fav.property for fav in favorites]
    context = {
        'properties': favorite_properties,
        'title': 'My Favorite Properties',
        'favorites_page': True
    }
    return render(request, 'services/favorites.html', context)

@login_required
def get_favorite_status(request, property_id):
    """Check if a property is in the user's favorites."""
    property_obj = get_object_or_404(BuyProperties, id=property_id)
    is_favorite = UserFavorite.objects.filter(
        user=request.user,
        property=property_obj
    ).exists()
    return JsonResponse({
        'is_favorite': is_favorite
    })
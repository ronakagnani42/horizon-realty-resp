from django.contrib import admin
from .models import *
from django.utils.html import format_html

@admin.register(PropertyLocation)
class PropertyLocationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 3

class PropertyVideoInline(admin.TabularInline):
    model = PropertyVideo
    extra = 1

@admin.register(NearbyPlaces)
class NearbyAmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'distance_value', 'distance_unit')
    search_fields = ('name',)
    list_filter = ('distance_unit',)


@admin.register(FeatureAmenity)
class FeatureAmenityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(BuyProperties)
class BuyPropertiesAdmin(admin.ModelAdmin):
    inlines = [PropertyImageInline, PropertyVideoInline]
    list_display = ('project_name', 'property_type', 'category', 'area', 'budget_range', 'possession_date', 
                   'number_of_units', 'number_of_lifts', 'number_of_storey', 'salient_features', 
                   'locations', 'has_brochure','is_property_active')
    list_filter = ('project_name', 'property_type', 'category', 'locations', 'min_budget_unit', 'max_budget_unit','is_property_active')
    search_fields = ('project_name', 'property_type', 'category', 'locations__name')
    filter_horizontal = ('nearby_amenities', 'feature_amenities')
    prepopulated_fields = {'slug': ('project_name',)}
    
    def budget_range(self, obj):
        min_budget_str = f"{obj.min_budget} {obj.min_budget_unit.capitalize()}"
        max_budget_str = f"{obj.max_budget} {obj.max_budget_unit.capitalize()}"
        return f"{min_budget_str} to {max_budget_str}"
    budget_range.short_description = "Budget Range"
    
    def has_brochure(self, obj):
        return bool(obj.brochure_pdf)
    has_brochure.boolean = True
    has_brochure.short_description = "Brochure"

@admin.register(SellResidentialProperties)
class SellResidentialPropertiesAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'category', 'area', 'budget','floor_num','unit_num','property_subtype', 'locations','additional_details', 'is_approved', 'image_preview', 'contact_email', 'contact_name','contact_number')
    list_filter = ('status', 'category', 'locations', 'is_approved')
    search_fields = ('project_name', 'category', 'locations__location_name')
    readonly_fields = ('image_tag', 'video_tag')
    
    def status_display(self, obj):
        """Display status with proper formatting"""
        if obj.status and obj.status != '':
            return dict(obj.STATUS_CHOICES)[obj.status]
        return "-"
    status_display.short_description = 'Status'

    def image_preview(self, obj):
        """Show small image preview in list view"""
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image'

    def image_tag(self, obj):
        """Show larger image in detail view"""
        if obj.image:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 300px;" />', obj.image.url)
        return "No Image"
    image_tag.short_description = 'Current Image'

    def video_tag(self, obj):
        """Show video player in detail view"""
        if obj.video:
            return format_html(
                '<video width="300" height="200" controls><source src="{}" type="video/mp4">Your browser does not support the video tag.</video>',
                obj.video.url
            )
        return "No Video"
    video_tag.short_description = 'Current Video'

@admin.register(SellCommercialProperties)
class SellCommercialPropertiesAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'status_display', 'area', 'budget','floor_num','unit_num','property_subtype', 'locations','additional_details', 'is_approved', 'image_preview', 'contact_email', 'contact_name','contact_number')
    list_filter = ('status', 'locations', 'is_approved')
    search_fields = ('project_name', 'locations__location_name')
    readonly_fields = ('image_tag', 'video_tag')
    
    def status_display(self, obj):
        """Display status with proper formatting"""
        if obj.status and obj.status != '':
            status_dict = dict(obj.STATUS_CHOICES)
            return status_dict.get(obj.status, f"Unknown ({obj.status})")
        return "-"

    def image_preview(self, obj):
        """Show small image preview in list view"""
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image'

    def image_tag(self, obj):
        """Show larger image in detail view"""
        if obj.image:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 300px;" />', obj.image.url)
        return "No Image"
    image_tag.short_description = 'Current Image'

    def video_tag(self, obj):
        """Show video player in detail view"""
        if obj.video:
            return format_html(
                '<video width="300" height="200" controls><source src="{}" type="video/mp4">Your browser does not support the video tag.</video>',
                obj.video.url
            )
        return "No Video"
    video_tag.short_description = 'Current Video'


    
@admin.register(InteriorDesignRequest)
class InteriorDesignRequestAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'phone_number', 
        'property_types',
        'service_types',
        'sqft',
        'created_at',
    ]
    
    list_filter = [
        'created_at',
        'property_types',
        'service_types'
    ]
    
    search_fields = [
        'name',
        'phone_number'
    ]
    
    fields = [
        'name', 
        'phone_number', 
        'property_types', 
        'sqft', 
        'service_types'
    ]
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request)


@admin.register(CheckOurWorkBrochure)
class CheckOurWorkBrochureAdmin(admin.ModelAdmin):
    list_display = [
        'get_file_name', 
        'get_file_size', 
        'is_active', 
        'uploaded_at'
    ]
    list_filter = [
        'is_active', 
        'uploaded_at'
    ]
    
    readonly_fields = [
        'uploaded_at', 
        'get_file_name', 
        'get_file_size'
    ]
    def get_file_name(self, obj):
        return obj.get_file_name()
    get_file_name.short_description = 'File Name'
    
    def get_file_size(self, obj):
        return obj.get_file_size()
    get_file_size.short_description = 'File Size'

@admin.register(PropertyInquiry)
class PropertyInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'property', 'created_at')
    list_filter = ('created_at', 'property__property_type', 'property__locations')
    search_fields = ('name', 'email', 'phone', 'message')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('property')

@admin.register(PropertyCalculatorInquiry)
class PropertyCalculatorInquiryAdmin(admin.ModelAdmin):
    list_display = ('title', 'property_type', 'floor', 'location', 'owner_name', 'phone_number', 'area', 'created_at')
    list_filter = ('title', 'property_type', 'location', 'created_at')
    search_fields = ('title', 'property_type', 'location', 'owner_name', 'phone_number', 'flat_society_name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'property_type', 'owner_name', 'phone_number')
        }),
        ('Property Details', {
            'fields': ('location', 'flat_society_name', 'floor', 'area', 'property_life')
        }),
        ('Media Files', {
            'fields': ('photo', 'document')
        }),
        ('Additional Information', {
            'fields': ('additional_info',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
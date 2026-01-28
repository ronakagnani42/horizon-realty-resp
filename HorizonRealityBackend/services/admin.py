from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.urls import reverse
from django.http import HttpResponse
import csv
from datetime import datetime
from .models import (
    PropertyLocation, NearbyPlaces, FeatureAmenity, BuyProperties,
    PropertyImage, PropertyVideo, SellResidentialProperties,
    SellCommercialProperties, InteriorDesignRequest, CheckOurWorkBrochure,
    PropertyInquiry, PropertyCalculatorInquiry, UserFavorite
)


# ============================================================================
# INLINE ADMINS
# ============================================================================

class PropertyImageInline(admin.TabularInline):
    """Inline admin for property images."""
    model = PropertyImage
    extra = 1
    min_num = 0
    fields = ('image_preview', 'image', 'caption', 'is_primary')
    readonly_fields = ('image_preview',)
    classes = ('collapse',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="80" height="80" style="object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">No image</span>')
    image_preview.short_description = 'Preview'


class PropertyVideoInline(admin.TabularInline):
    """Inline admin for property videos."""
    model = PropertyVideo
    extra = 1
    min_num = 0
    fields = ('thumbnail_preview', 'video', 'thumbnail', 'title')
    readonly_fields = ('thumbnail_preview',)
    classes = ('collapse',)
    
    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" width="80" height="60" style="object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />',
                obj.thumbnail.url
            )
        return format_html('<span style="color: #999;">No thumbnail</span>')
    thumbnail_preview.short_description = 'Thumbnail'


# ============================================================================
# PROPERTY LOCATION ADMIN
# ============================================================================

@admin.register(PropertyLocation)
class PropertyLocationAdmin(admin.ModelAdmin):
    """Enhanced admin for Property Locations."""
    
    list_display = ('name_with_icon', 'property_count')
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 30
    
    actions = ['duplicate_locations', 'export_as_csv']
    
    def name_with_icon(self, obj):
        return format_html(
            '<span style="font-weight: 500;">📍 {}</span>',
            obj.name
        )
    name_with_icon.short_description = 'Location Name'
    name_with_icon.admin_order_field = 'name'
    
    def property_count(self, obj):
        count = obj.buyproperties_set.count()
        if count > 0:
            return format_html(
                '<span style="background: #2196F3; color: white; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">🏘️ {} properties</span>',
                count
            )
        return format_html('<span style="color: #999;">No properties</span>')
    property_count.short_description = 'Properties'
    
    @admin.action(description='📋 Duplicate selected locations')
    def duplicate_locations(self, request, queryset):
        duplicated_count = 0
        for location in queryset:
            location.pk = None
            location.name = f"{location.name} (Copy)"
            location.save()
            duplicated_count += 1
        self.message_user(request, f'{duplicated_count} location(s) duplicated successfully.')
    
    @admin.action(description='📥 Export as CSV')
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="property_locations_{timestamp}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Location Name', 'Properties Count'])
        
        for location in queryset:
            writer.writerow([
                location.id,
                location.name,
                location.buyproperties_set.count()
            ])
        
        self.message_user(request, f'{queryset.count()} location(s) exported successfully.')
        return response


# ============================================================================
# NEARBY PLACES ADMIN
# ============================================================================

@admin.register(NearbyPlaces)
class NearbyPlacesAdmin(admin.ModelAdmin):
    """Enhanced admin for Nearby Places."""
    
    list_display = ('name_with_icon', 'distance_badge', 'unit_badge')
    list_filter = ('distance_unit',)
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 30
    
    fields = ('name', 'distance_value', 'distance_unit')
    
    actions = ['duplicate_places', 'export_as_csv']
    
    def name_with_icon(self, obj):
        return format_html(
            '<span style="font-weight: 500;">🏢 {}</span>',
            obj.name
        )
    name_with_icon.short_description = 'Place Name'
    name_with_icon.admin_order_field = 'name'
    
    def distance_badge(self, obj):
        return format_html(
            '<span style="background: #FF9800; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">{} {}</span>',
            obj.distance_value, obj.get_distance_unit_display()
        )
    distance_badge.short_description = 'Distance'
    
    def unit_badge(self, obj):
        color = '#4CAF50' if obj.distance_unit == 'km' else '#2196F3'
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            color, obj.get_distance_unit_display()
        )
    unit_badge.short_description = 'Unit'
    
    @admin.action(description='📋 Duplicate selected places')
    def duplicate_places(self, request, queryset):
        duplicated_count = 0
        for place in queryset:
            place.pk = None
            place.name = f"{place.name} (Copy)"
            place.save()
            duplicated_count += 1
        self.message_user(request, f'{duplicated_count} place(s) duplicated successfully.')
    
    @admin.action(description='📥 Export as CSV')
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="nearby_places_{timestamp}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Name', 'Distance Value', 'Distance Unit'])
        
        for place in queryset:
            writer.writerow([
                place.id,
                place.name,
                place.distance_value,
                place.get_distance_unit_display()
            ])
        
        self.message_user(request, f'{queryset.count()} place(s) exported successfully.')
        return response


# ============================================================================
# FEATURE AMENITY ADMIN
# ============================================================================

@admin.register(FeatureAmenity)
class FeatureAmenityAdmin(admin.ModelAdmin):
    """Enhanced admin for Feature Amenities."""
    
    list_display = ('name_with_icon', 'properties_count')
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 30
    
    actions = ['duplicate_amenities', 'export_as_csv']
    
    def name_with_icon(self, obj):
        return format_html(
            '<span style="font-weight: 500;">✨ {}</span>',
            obj.name
        )
    name_with_icon.short_description = 'Amenity Name'
    name_with_icon.admin_order_field = 'name'
    
    def properties_count(self, obj):
        count = obj.properties.count()
        if count > 0:
            return format_html(
                '<span style="background: #9C27B0; color: white; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">🏠 {} properties</span>',
                count
            )
        return format_html('<span style="color: #999;">No properties</span>')
    properties_count.short_description = 'Used In'
    
    @admin.action(description='📋 Duplicate selected amenities')
    def duplicate_amenities(self, request, queryset):
        duplicated_count = 0
        for amenity in queryset:
            amenity.pk = None
            amenity.name = f"{amenity.name} (Copy)"
            amenity.save()
            duplicated_count += 1
        self.message_user(request, f'{duplicated_count} amenity(ies) duplicated successfully.')
    
    @admin.action(description='📥 Export as CSV')
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="feature_amenities_{timestamp}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Name', 'Properties Count'])
        
        for amenity in queryset:
            writer.writerow([
                amenity.id,
                amenity.name,
                amenity.properties.count()
            ])
        
        self.message_user(request, f'{queryset.count()} amenity(ies) exported successfully.')
        return response


# ============================================================================
# BUY PROPERTIES ADMIN
# ============================================================================

@admin.register(BuyProperties)
class BuyPropertiesAdmin(admin.ModelAdmin):
    """Enhanced admin for Buy Properties."""
    
    list_display = (
        'project_name_with_icon',
        'property_type_badge',
        'category_badge',
        'area_display',
        'budget_range_display',
        'location_display',
        'status_badge',
        'media_count',
        'created_at'
    )
    
    list_filter = (
        'property_type',
        'category',
        'status',
        'is_property_active',
        'locations',
        'min_budget_unit',
        'max_budget_unit',
        'created_at'
    )
    
    search_fields = (
        'project_name',
        'slug',
        'locations__name',
        'salient_features'
    )
    
    fields = (
        'project_name',
        'slug',
        'property_type',
        'status',
        'category',
        'configuration',
        'commercial_type',
        'floor',
        'rent_per_sqft',
        'lockin_period',
        'increment',
        'furnishing',
        'area',
        'area_in_sqyards',
        'min_budget',
        'min_budget_unit',
        'max_budget',
        'max_budget_unit',
        'locations',
        'image',
        'main_image_preview',
        'brochure_pdf',
        'possession_date',
        'number_of_units',
        'number_of_lifts',
        'number_of_storey',
        'salient_features',
        'nearby_amenities',
        'feature_amenities',
        'is_property_active',
        'created_at'
    )
    
    readonly_fields = ('main_image_preview', 'created_at')
    prepopulated_fields = {'slug': ('project_name',)}
    filter_horizontal = ('nearby_amenities', 'feature_amenities')
    
    inlines = [PropertyImageInline, PropertyVideoInline]
    
    ordering = ('-created_at',)
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    actions = ['activate_properties', 'deactivate_properties', 'duplicate_properties', 'export_as_csv']
    
    # Custom display methods
    
    def project_name_with_icon(self, obj):
        icon = '🏠' if obj.property_type == 'residential' else '🏢'
        return format_html(
            '<span style="font-weight: 500;">{} {}</span>',
            icon, obj.project_name or 'Unnamed Property'
        )
    project_name_with_icon.short_description = 'Project Name'
    project_name_with_icon.admin_order_field = 'project_name'
    
    def property_type_badge(self, obj):
        color = '#4CAF50' if obj.property_type == 'residential' else '#2196F3'
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            color, obj.get_property_type_display()
        )
    property_type_badge.short_description = 'Type'
    property_type_badge.admin_order_field = 'property_type'
    
    def category_badge(self, obj):
        return format_html(
            '<span style="background: #673AB7; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            obj.get_category_display()
        )
    category_badge.short_description = 'Category'
    category_badge.admin_order_field = 'category'
    
    def area_display(self, obj):
        return format_html(
            '<span style="font-weight: 500;">{} sqft</span>',
            obj.area
        )
    area_display.short_description = 'Area'
    area_display.admin_order_field = 'area'
    
    def budget_range_display(self, obj):
        if obj.min_budget and obj.max_budget:
            return format_html(
                '<span style="background: #FF9800; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">₹{} - {} {}</span>',
                obj.min_budget, obj.max_budget, obj.max_budget_unit.upper()
            )
        return format_html('<span style="color: #999;">Not set</span>')
    budget_range_display.short_description = 'Budget Range'
    
    def location_display(self, obj):
        if obj.locations:
            return format_html(
                '<span style="font-weight: 500;">📍 {}</span>',
                obj.locations.name
            )
        return format_html('<span style="color: #999;">No location</span>')
    location_display.short_description = 'Location'
    location_display.admin_order_field = 'locations__name'
    
    def status_badge(self, obj):
        if obj.is_property_active:
            return format_html(
                '<span style="background: #4CAF50; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">✓ Active</span>'
            )
        return format_html(
            '<span style="background: #f44336; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">✗ Inactive</span>'
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'is_property_active'
    
    def media_count(self, obj):
        images = obj.images.count()
        videos = obj.videos.count()
        return format_html(
            '<span style="background: #00BCD4; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">📷 {} 🎥 {}</span>',
            images, videos
        )
    media_count.short_description = 'Media'
    
    def main_image_preview(self, obj):
        if obj.image:
            return format_html(
                '<div style="margin-top: 10px;">'
                '<img src="{}" style="max-width: 400px; max-height: 300px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" />'
                '</div>',
                obj.image.url
            )
        return format_html('<p style="color: #999;">No image uploaded</p>')
    main_image_preview.short_description = 'Main Image Preview'
    
    # Actions
    
    @admin.action(description='✓ Activate selected properties')
    def activate_properties(self, request, queryset):
        updated = queryset.update(is_property_active=True)
        self.message_user(request, f'{updated} property(ies) activated.')
    
    @admin.action(description='✗ Deactivate selected properties')
    def deactivate_properties(self, request, queryset):
        updated = queryset.update(is_property_active=False)
        self.message_user(request, f'{updated} property(ies) deactivated.')
    
    @admin.action(description='📋 Duplicate selected properties')
    def duplicate_properties(self, request, queryset):
        duplicated_count = 0
        for prop in queryset:
            # Store related data
            original_images = list(prop.images.all())
            original_videos = list(prop.videos.all())
            nearby = list(prop.nearby_amenities.all())
            features = list(prop.feature_amenities.all())
            
            # Duplicate property
            prop.pk = None
            prop.project_name = f"{prop.project_name} (Copy)" if prop.project_name else "Copy"
            prop.slug = None
            prop.is_property_active = False
            prop.save()
            
            # Restore many-to-many relationships
            prop.nearby_amenities.set(nearby)
            prop.feature_amenities.set(features)
            
            # Duplicate images
            for img in original_images:
                img.pk = None
                img.property = prop
                img.save()
            
            # Duplicate videos
            for video in original_videos:
                video.pk = None
                video.property = prop
                video.save()
            
            duplicated_count += 1
        
        self.message_user(request, f'{duplicated_count} property(ies) duplicated successfully.')
    
    @admin.action(description='📥 Export as CSV')
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="buy_properties_{timestamp}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Project Name', 'Property Type', 'Category', 'Status',
            'Area (sqft)', 'Min Budget', 'Max Budget', 'Location',
            'Configuration', 'Commercial Type', 'Furnishing',
            'Is Active', 'Created At'
        ])
        
        for prop in queryset:
            writer.writerow([
                prop.id,
                prop.project_name or '',
                prop.get_property_type_display(),
                prop.get_category_display(),
                prop.get_status_display() if prop.status else '',
                prop.area,
                f"{prop.min_budget} {prop.min_budget_unit}" if prop.min_budget else '',
                f"{prop.max_budget} {prop.max_budget_unit}" if prop.max_budget else '',
                prop.locations.name if prop.locations else '',
                prop.get_configuration_display() if prop.configuration else '',
                prop.get_commercial_type_display() if prop.commercial_type else '',
                prop.get_furnishing_display() if prop.furnishing else '',
                'Yes' if prop.is_property_active else 'No',
                prop.created_at.strftime('%Y-%m-%d %H:%M:%S') if prop.created_at else ''
            ])
        
        self.message_user(request, f'{queryset.count()} property(ies) exported successfully.')
        return response
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('locations').prefetch_related('images', 'videos')


# ============================================================================
# SELL RESIDENTIAL PROPERTIES ADMIN
# ============================================================================

@admin.register(SellResidentialProperties)
class SellResidentialPropertiesAdmin(admin.ModelAdmin):
    """Enhanced admin for Sell Residential Properties."""
    
    list_display = (
        'project_name_with_icon',
        'status_badge',
        'category_badge',
        'area_display',
        'budget_display',
        'location_display',
        'floor_unit',
        'approval_badge',
        'contact_display',
        'image_preview'
    )
    
    list_filter = (
        'status',
        'category',
        'is_approved',
        'locations',
        'configuration'
    )
    
    search_fields = (
        'project_name',
        'contact_name',
        'contact_email',
        'contact_number',
        'locations__name'
    )
    
    fields = (
        'project_name',
        'status',
        'category',
        'configuration',
        'property_subtype',
        'area',
        'area_in_sqyards',
        'budget',
        'floor_num',
        'unit_num',
        'locations',
        'image',
        'large_image_preview',
        'video',
        'video_preview',
        'contact_name',
        'contact_email',
        'contact_number',
        'additional_details',
        'is_approved'
    )
    
    readonly_fields = ('large_image_preview', 'video_preview')
    
    ordering = ('-id',)
    list_per_page = 25
    
    actions = ['approve_properties', 'reject_properties', 'duplicate_properties', 'export_as_csv']
    
    # Custom display methods
    
    def project_name_with_icon(self, obj):
        return format_html(
            '<span style="font-weight: 500;">🏘️ {}</span>',
            obj.project_name
        )
    project_name_with_icon.short_description = 'Project Name'
    project_name_with_icon.admin_order_field = 'project_name'
    
    def status_badge(self, obj):
        colors = {'resale': '#4CAF50', 'rent': '#FF9800', 'lease': '#2196F3'}
        color = colors.get(obj.status, '#999')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            color, obj.get_status_display() if obj.status else 'N/A'
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def category_badge(self, obj):
        return format_html(
            '<span style="background: #673AB7; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            obj.get_category_display()
        )
    category_badge.short_description = 'Category'
    
    def area_display(self, obj):
        return format_html(
            '<span style="font-weight: 500;">{} sqft</span>',
            obj.area
        )
    area_display.short_description = 'Area'
    
    def budget_display(self, obj):
        return format_html(
            '<span style="background: #FF9800; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">₹{:,}</span>',
            obj.budget
        )
    budget_display.short_description = 'Budget'
    
    def location_display(self, obj):
        if obj.locations:
            return format_html('<span style="font-weight: 500;">📍 {}</span>', obj.locations.name)
        return format_html('<span style="color: #999;">No location</span>')
    location_display.short_description = 'Location'
    
    def floor_unit(self, obj):
        parts = []
        if obj.floor_num:
            parts.append(f"Floor: {obj.floor_num}")
        if obj.unit_num:
            parts.append(f"Unit: {obj.unit_num}")
        if parts:
            return format_html('<span style="font-size: 11px;">{}</span>', ' | '.join(parts))
        return format_html('<span style="color: #999;">-</span>')
    floor_unit.short_description = 'Floor/Unit'
    
    def approval_badge(self, obj):
        if obj.is_approved:
            return format_html(
                '<span style="background: #4CAF50; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">✓ Approved</span>'
            )
        return format_html(
            '<span style="background: #f44336; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">⏳ Pending</span>'
        )
    approval_badge.short_description = 'Approval'
    approval_badge.admin_order_field = 'is_approved'
    
    def contact_display(self, obj):
        return format_html(
            '<div style="font-size: 11px;">'
            '<div style="font-weight: 500;">{}</div>'
            '<div style="color: #666;">📧 {}</div>'
            '<div style="color: #666;">📞 {}</div>'
            '</div>',
            obj.contact_name or 'N/A',
            obj.contact_email,
            obj.contact_number or 'N/A'
        )
    contact_display.short_description = 'Contact'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">No image</span>')
    image_preview.short_description = 'Image'
    
    def large_image_preview(self, obj):
        if obj.image:
            return format_html(
                '<div style="margin-top: 10px;">'
                '<img src="{}" style="max-width: 500px; max-height: 400px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" />'
                '</div>',
                obj.image.url
            )
        return format_html('<p style="color: #999;">No image uploaded</p>')
    large_image_preview.short_description = 'Image Preview'
    
    def video_preview(self, obj):
        if obj.video:
            return format_html(
                '<video width="400" height="300" controls style="border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">'
                '<source src="{}" type="video/mp4">Your browser does not support the video tag.'
                '</video>',
                obj.video.url
            )
        return format_html('<p style="color: #999;">No video uploaded</p>')
    video_preview.short_description = 'Video Preview'
    
    # Actions
    
    @admin.action(description='✓ Approve selected properties')
    def approve_properties(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} property(ies) approved.')
    
    @admin.action(description='✗ Reject selected properties')
    def reject_properties(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} property(ies) rejected.')
    
    @admin.action(description='📋 Duplicate selected properties')
    def duplicate_properties(self, request, queryset):
        duplicated_count = 0
        for prop in queryset:
            prop.pk = None
            prop.project_name = f"{prop.project_name} (Copy)"
            prop.is_approved = False
            prop.save()
            duplicated_count += 1
        self.message_user(request, f'{duplicated_count} property(ies) duplicated successfully.')
    
    @admin.action(description='📥 Export as CSV')
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="sell_residential_{timestamp}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Project Name', 'Status', 'Category', 'Configuration',
            'Area (sqft)', 'Budget (INR)', 'Floor', 'Unit', 'Location',
            'Contact Name', 'Contact Email', 'Contact Number',
            'Is Approved', 'Additional Details'
        ])
        
        for prop in queryset:
            writer.writerow([
                prop.id,
                prop.project_name,
                prop.get_status_display() if prop.status else '',
                prop.get_category_display(),
                prop.get_configuration_display() if prop.configuration else '',
                prop.area,
                prop.budget,
                prop.floor_num or '',
                prop.unit_num or '',
                prop.locations.name if prop.locations else '',
                prop.contact_name or '',
                prop.contact_email,
                prop.contact_number or '',
                'Yes' if prop.is_approved else 'No',
                prop.additional_details or ''
            ])
        
        self.message_user(request, f'{queryset.count()} property(ies) exported successfully.')
        return response


# ============================================================================
# SELL COMMERCIAL PROPERTIES ADMIN
# ============================================================================

@admin.register(SellCommercialProperties)
class SellCommercialPropertiesAdmin(admin.ModelAdmin):
    """Enhanced admin for Sell Commercial Properties."""
    
    list_display = (
        'project_name_with_icon',
        'commercial_type_badge',
        'status_badge',
        'furnishing_badge',
        'area_display',
        'budget_display',
        'location_display',
        'floor_unit',
        'approval_badge',
        'contact_display',
        'image_preview'
    )
    
    list_filter = (
        'status',
        'commercial_type',
        'furnishing',
        'is_approved',
        'locations'
    )
    
    search_fields = (
        'project_name',
        'contact_name',
        'contact_email',
        'contact_number',
        'locations__name'
    )
    
    fields = (
        'project_name',
        'commercial_type',
        'property_subtype',
        'furnishing',
        'status',
        'area',
        'area_in_sqyards',
        'budget',
        'floor_num',
        'unit_num',
        'locations',
        'image',
        'large_image_preview',
        'video',
        'video_preview',
        'contact_name',
        'contact_email',
        'contact_number',
        'additional_details',
        'is_approved'
    )
    
    readonly_fields = ('large_image_preview', 'video_preview')
    
    ordering = ('-id',)
    list_per_page = 25
    
    actions = ['approve_properties', 'reject_properties', 'duplicate_properties', 'export_as_csv']
    
    # Custom display methods
    
    def project_name_with_icon(self, obj):
        return format_html(
            '<span style="font-weight: 500;">🏢 {}</span>',
            obj.project_name
        )
    project_name_with_icon.short_description = 'Project Name'
    project_name_with_icon.admin_order_field = 'project_name'
    
    def commercial_type_badge(self, obj):
        colors = {
            'showroom': '#FF5722',
            'office': '#2196F3',
            'shop': '#4CAF50',
            'corporate_floors': '#9C27B0',
            'other': '#607D8B'
        }
        color = colors.get(obj.commercial_type, '#999')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            color, obj.get_commercial_type_display() if obj.commercial_type else 'N/A'
        )
    commercial_type_badge.short_description = 'Type'
    commercial_type_badge.admin_order_field = 'commercial_type'
    
    def status_badge(self, obj):
        colors = {'resale': '#4CAF50', 'rent': '#FF9800', 'lease': '#2196F3'}
        color = colors.get(obj.status, '#999')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            color, obj.get_status_display() if obj.status else 'N/A'
        )
    status_badge.short_description = 'Status'
    
    def furnishing_badge(self, obj):
        colors = {
            'furnished': '#4CAF50',
            'semi-furnished': '#FF9800',
            'unfurnished': '#999'
        }
        color = colors.get(obj.furnishing, '#999')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            color, obj.get_furnishing_display() if obj.furnishing else 'N/A'
        )
    furnishing_badge.short_description = 'Furnishing'
    
    def area_display(self, obj):
        return format_html('<span style="font-weight: 500;">{} sqft</span>', obj.area)
    area_display.short_description = 'Area'
    
    def budget_display(self, obj):
        return format_html(
            '<span style="background: #FF9800; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">₹{:,}</span>',
            obj.budget
        )
    budget_display.short_description = 'Budget'
    
    def location_display(self, obj):
        if obj.locations:
            return format_html('<span style="font-weight: 500;">📍 {}</span>', obj.locations.name)
        return format_html('<span style="color: #999;">No location</span>')
    location_display.short_description = 'Location'
    
    def floor_unit(self, obj):
        parts = []
        if obj.floor_num:
            parts.append(f"Floor: {obj.floor_num}")
        if obj.unit_num:
            parts.append(f"Unit: {obj.unit_num}")
        if parts:
            return format_html('<span style="font-size: 11px;">{}</span>', ' | '.join(parts))
        return format_html('<span style="color: #999;">-</span>')
    floor_unit.short_description = 'Floor/Unit'
    
    def approval_badge(self, obj):
        if obj.is_approved:
            return format_html(
                '<span style="background: #4CAF50; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">✓ Approved</span>'
            )
        return format_html(
            '<span style="background: #f44336; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">⏳ Pending</span>'
        )
    approval_badge.short_description = 'Approval'
    approval_badge.admin_order_field = 'is_approved'
    
    def contact_display(self, obj):
        return format_html(
            '<div style="font-size: 11px;">'
            '<div style="font-weight: 500;">{}</div>'
            '<div style="color: #666;">📧 {}</div>'
            '<div style="color: #666;">📞 {}</div>'
            '</div>',
            obj.contact_name or 'N/A',
            obj.contact_email,
            obj.contact_number or 'N/A'
        )
    contact_display.short_description = 'Contact'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">No image</span>')
    image_preview.short_description = 'Image'
    
    def large_image_preview(self, obj):
        if obj.image:
            return format_html(
                '<div style="margin-top: 10px;">'
                '<img src="{}" style="max-width: 500px; max-height: 400px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" />'
                '</div>',
                obj.image.url
            )
        return format_html('<p style="color: #999;">No image uploaded</p>')
    large_image_preview.short_description = 'Image Preview'
    
    def video_preview(self, obj):
        if obj.video:
            return format_html(
                '<video width="400" height="300" controls style="border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">'
                '<source src="{}" type="video/mp4">Your browser does not support the video tag.'
                '</video>',
                obj.video.url
            )
        return format_html('<p style="color: #999;">No video uploaded</p>')
    video_preview.short_description = 'Video Preview'
    
    # Actions
    
    @admin.action(description='✓ Approve selected properties')
    def approve_properties(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} property(ies) approved.')
    
    @admin.action(description='✗ Reject selected properties')
    def reject_properties(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} property(ies) rejected.')
    
    @admin.action(description='📋 Duplicate selected properties')
    def duplicate_properties(self, request, queryset):
        duplicated_count = 0
        for prop in queryset:
            prop.pk = None
            prop.project_name = f"{prop.project_name} (Copy)"
            prop.is_approved = False
            prop.save()
            duplicated_count += 1
        self.message_user(request, f'{duplicated_count} property(ies) duplicated successfully.')
    
    @admin.action(description='📥 Export as CSV')
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="sell_commercial_{timestamp}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Project Name', 'Commercial Type', 'Status', 'Furnishing',
            'Area (sqft)', 'Budget (INR)', 'Floor', 'Unit', 'Location',
            'Contact Name', 'Contact Email', 'Contact Number',
            'Is Approved', 'Additional Details'
        ])
        
        for prop in queryset:
            writer.writerow([
                prop.id,
                prop.project_name,
                prop.get_commercial_type_display() if prop.commercial_type else '',
                prop.get_status_display() if prop.status else '',
                prop.get_furnishing_display() if prop.furnishing else '',
                prop.area,
                prop.budget,
                prop.floor_num or '',
                prop.unit_num or '',
                prop.locations.name if prop.locations else '',
                prop.contact_name or '',
                prop.contact_email,
                prop.contact_number or '',
                'Yes' if prop.is_approved else 'No',
                prop.additional_details or ''
            ])
        
        self.message_user(request, f'{queryset.count()} property(ies) exported successfully.')
        return response


# ============================================================================
# INTERIOR DESIGN REQUEST ADMIN
# ============================================================================

@admin.register(InteriorDesignRequest)
class InteriorDesignRequestAdmin(admin.ModelAdmin):
    """Enhanced admin for Interior Design Requests."""
    
    list_display = (
        'name_with_icon',
        'phone_display',
        'property_type_badge',
        'service_type_badge',
        'sqft_display',
        'created_at'
    )
    
    list_filter = (
        'property_types',
        'service_types',
        'created_at'
    )
    
    search_fields = (
        'name',
        'phone_number'
    )
    
    fields = (
        'name',
        'phone_number',
        'property_types',
        'sqft',
        'service_types',
        'created_at',
        'updated_at'
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    ordering = ('-created_at',)
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    actions = ['export_as_csv']
    
    # Custom display methods
    
    def name_with_icon(self, obj):
        return format_html(
            '<span style="font-weight: 500;">👤 {}</span>',
            obj.name
        )
    name_with_icon.short_description = 'Name'
    name_with_icon.admin_order_field = 'name'
    
    def phone_display(self, obj):
        return format_html(
            '<a href="tel:{}" style="color: #4CAF50; text-decoration: none; font-weight: 500;">📞 {}</a>',
            obj.phone_number, obj.phone_number
        )
    phone_display.short_description = 'Phone'
    
    def property_type_badge(self, obj):
        colors = {'flat': '#2196F3', 'bungalow': '#4CAF50', 'penthouse': '#9C27B0'}
        color = colors.get(obj.property_types, '#999')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            color, obj.get_property_types_display()
        )
    property_type_badge.short_description = 'Property Type'
    
    def service_type_badge(self, obj):
        colors = {'turnkey': '#FF9800', 'consultancy': '#00BCD4'}
        color = colors.get(obj.service_types, '#999')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            color, obj.get_service_types_display()
        )
    service_type_badge.short_description = 'Service Type'
    
    def sqft_display(self, obj):
        if obj.sqft:
            return format_html(
                '<span style="font-weight: 500;">{} sqft</span>',
                obj.sqft
            )
        return format_html('<span style="color: #999;">Not specified</span>')
    sqft_display.short_description = 'Area'
    
    @admin.action(description='📥 Export as CSV')
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="interior_requests_{timestamp}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Name', 'Phone Number', 'Property Type',
            'Square Feet', 'Service Type', 'Created At'
        ])
        
        for request_obj in queryset:
            writer.writerow([
                request_obj.id,
                request_obj.name,
                request_obj.phone_number,
                request_obj.get_property_types_display(),
                request_obj.sqft or '',
                request_obj.get_service_types_display(),
                request_obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        self.message_user(request, f'{queryset.count()} request(s) exported successfully.')
        return response


# ============================================================================
# CHECK OUR WORK BROCHURE ADMIN
# ============================================================================

@admin.register(CheckOurWorkBrochure)
class CheckOurWorkBrochureAdmin(admin.ModelAdmin):
    """Enhanced admin for Check Our Work Brochures."""
    
    list_display = (
        'file_name_display',
        'file_size_display',
        'status_badge',
        'uploaded_at'
    )
    
    list_filter = (
        'is_active',
        'uploaded_at'
    )
    
    fields = (
        'check_our_work_brochure',
        'file_preview',
        'is_active',
        'uploaded_at'
    )
    
    readonly_fields = ('file_preview', 'uploaded_at')
    
    ordering = ('-uploaded_at',)
    list_per_page = 25
    date_hierarchy = 'uploaded_at'
    
    actions = ['activate_brochures', 'deactivate_brochures', 'export_as_csv']
    
    # Custom display methods
    
    def file_name_display(self, obj):
        return format_html(
            '<span style="font-weight: 500;">📄 {}</span>',
            obj.get_file_name()
        )
    file_name_display.short_description = 'File Name'
    
    def file_size_display(self, obj):
        return format_html(
            '<span style="background: #00BCD4; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            obj.get_file_size()
        )
    file_size_display.short_description = 'File Size'
    
    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #4CAF50; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">✓ Active</span>'
            )
        return format_html(
            '<span style="background: #f44336; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">✗ Inactive</span>'
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'is_active'
    
    def file_preview(self, obj):
        if obj.check_our_work_brochure:
            return format_html(
                '<div style="margin-top: 10px;">'
                '<a href="{}" target="_blank" style="background: #2196F3; color: white; padding: 10px 20px; border-radius: 4px; text-decoration: none; display: inline-block;">📥 Download Brochure</a>'
                '<p style="margin-top: 10px; color: #666;">File: {}</p>'
                '<p style="color: #666;">Size: {}</p>'
                '</div>',
                obj.check_our_work_brochure.url,
                obj.get_file_name(),
                obj.get_file_size()
            )
        return format_html('<p style="color: #999;">No file uploaded</p>')
    file_preview.short_description = 'File Preview'
    
    # Actions
    
    @admin.action(description='✓ Activate brochures')
    def activate_brochures(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} brochure(s) activated.')
    
    @admin.action(description='✗ Deactivate brochures')
    def deactivate_brochures(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} brochure(s) deactivated.')
    
    @admin.action(description='📥 Export as CSV')
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="brochures_{timestamp}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'File Name', 'File Size', 'Is Active', 'Uploaded At'])
        
        for brochure in queryset:
            writer.writerow([
                brochure.id,
                brochure.get_file_name(),
                brochure.get_file_size(),
                'Yes' if brochure.is_active else 'No',
                brochure.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        self.message_user(request, f'{queryset.count()} brochure(s) exported successfully.')
        return response


# ============================================================================
# PROPERTY INQUIRY ADMIN
# ============================================================================

@admin.register(PropertyInquiry)
class PropertyInquiryAdmin(admin.ModelAdmin):
    """Enhanced admin for Property Inquiries."""
    
    list_display = (
        'name_with_icon',
        'contact_info',
        'property_link',
        'message_preview',
        'created_at'
    )
    
    list_filter = (
        'created_at',
        'property__property_type',
        'property__locations'
    )
    
    search_fields = (
        'name',
        'email',
        'phone',
        'message',
        'property__project_name'
    )
    
    fields = (
        'property',
        'property_details',
        'name',
        'email',
        'phone',
        'message',
        'created_at'
    )
    
    readonly_fields = ('property_details', 'created_at')
    
    ordering = ('-created_at',)
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    actions = ['export_as_csv']
    
    # Custom display methods
    
    def name_with_icon(self, obj):
        return format_html(
            '<span style="font-weight: 500;">👤 {}</span>',
            obj.name
        )
    name_with_icon.short_description = 'Name'
    name_with_icon.admin_order_field = 'name'
    
    def contact_info(self, obj):
        return format_html(
            '<div style="font-size: 11px;">'
            '<div style="color: #666;">📧 {}</div>'
            '<div style="color: #666;">📞 {}</div>'
            '</div>',
            obj.email,
            obj.phone
        )
    contact_info.short_description = 'Contact'
    
    def property_link(self, obj):
        url = reverse('admin:properties_buyproperties_change', args=[obj.property.pk])
        return format_html(
            '<a href="{}" style="color: #2196F3; text-decoration: none; font-weight: 500;">🏠 {}</a>',
            url, obj.property.project_name or 'View Property'
        )
    property_link.short_description = 'Property'
    
    def message_preview(self, obj):
        if obj.message and len(obj.message) > 60:
            return format_html(
                '<span style="font-style: italic;" title="{}">{}<span style="color: #999;">...</span></span>',
                obj.message, obj.message[:60]
            )
        return format_html('<span style="font-style: italic;">{}</span>', obj.message or 'No message')
    message_preview.short_description = 'Message'
    
    def property_details(self, obj):
        return format_html(
            '<div style="margin-top: 10px; padding: 15px; background: #f5f5f5; border-radius: 8px;">'
            '<h4 style="margin-top: 0;">Property Details</h4>'
            '<p><strong>Project:</strong> {}</p>'
            '<p><strong>Type:</strong> {}</p>'
            '<p><strong>Location:</strong> {}</p>'
            '<p><strong>Area:</strong> {} sqft</p>'
            '</div>',
            obj.property.project_name or 'N/A',
            obj.property.get_property_type_display(),
            obj.property.locations.name if obj.property.locations else 'N/A',
            obj.property.area
        )
    property_details.short_description = 'Property Info'
    
    @admin.action(description='📥 Export as CSV')
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="property_inquiries_{timestamp}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Name', 'Email', 'Phone', 'Property Name',
            'Property Type', 'Location', 'Message', 'Created At'
        ])
        
        for inquiry in queryset:
            writer.writerow([
                inquiry.id,
                inquiry.name,
                inquiry.email,
                inquiry.phone,
                inquiry.property.project_name or '',
                inquiry.property.get_property_type_display(),
                inquiry.property.locations.name if inquiry.property.locations else '',
                inquiry.message,
                inquiry.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        self.message_user(request, f'{queryset.count()} inquiry(ies) exported successfully.')
        return response
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('property', 'property__locations')


# ============================================================================
# PROPERTY CALCULATOR INQUIRY ADMIN
# ============================================================================

@admin.register(PropertyCalculatorInquiry)
class PropertyCalculatorInquiryAdmin(admin.ModelAdmin):
    """Enhanced admin for Property Calculator Inquiries."""
    
    list_display = (
        'title_badge',
        'property_type_display',
        'location_display',
        'owner_contact',
        'area_display',
        'floor_display',
        'created_at'
    )
    
    list_filter = (
        'title',
        'property_type',
        'created_at'
    )
    
    search_fields = (
        'owner_name',
        'phone_number',
        'location',
        'flat_society_name',
        'property_type'
    )
    
    fields = (
        'title',
        'property_type',
        'floor',
        'location',
        'flat_society_name',
        'area',
        'property_life',
        'owner_name',
        'phone_number',
        'photo',
        'photo_preview',
        'video',
        'video_preview',
        'document',
        'document_preview',
        'additional_info',
        'created_at',
        'updated_at'
    )
    
    readonly_fields = ('photo_preview', 'video_preview', 'document_preview', 'created_at', 'updated_at')
    
    ordering = ('-created_at',)
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    actions = ['export_as_csv']
    
    # Custom display methods
    
    def title_badge(self, obj):
        color = '#4CAF50' if obj.title == 'residential' else '#2196F3'
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            color, obj.get_title_display()
        )
    title_badge.short_description = 'Category'
    title_badge.admin_order_field = 'title'
    
    def property_type_display(self, obj):
        return format_html(
            '<span style="font-weight: 500;">{}</span>',
            obj.property_type
        )
    property_type_display.short_description = 'Property Type'
    
    def location_display(self, obj):
        return format_html(
            '<span style="font-weight: 500;">📍 {}</span>',
            obj.location
        )
    location_display.short_description = 'Location'
    location_display.admin_order_field = 'location'
    
    def owner_contact(self, obj):
        return format_html(
            '<div style="font-size: 11px;">'
            '<div style="font-weight: 500;">{}</div>'
            '<div style="color: #666;">📞 {}</div>'
            '</div>',
            obj.owner_name,
            obj.phone_number
        )
    owner_contact.short_description = 'Owner'
    
    def area_display(self, obj):
        return format_html(
            '<span style="background: #FF9800; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">{} sqft</span>',
            obj.area
        )
    area_display.short_description = 'Area'
    
    def floor_display(self, obj):
        if obj.floor:
            return format_html(
                '<span style="font-weight: 500;">Floor {}</span>',
                obj.floor
            )
        return format_html('<span style="color: #999;">-</span>')
    floor_display.short_description = 'Floor'
    
    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<div style="margin-top: 10px;">'
                '<img src="{}" style="max-width: 400px; max-height: 300px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" />'
                '</div>',
                obj.photo.url
            )
        return format_html('<p style="color: #999;">No photo uploaded</p>')
    photo_preview.short_description = 'Photo Preview'
    
    def video_preview(self, obj):
        if obj.video:
            return format_html(
                '<video width="400" height="300" controls style="border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">'
                '<source src="{}" type="video/mp4">Your browser does not support the video tag.'
                '</video>',
                obj.video.url
            )
        return format_html('<p style="color: #999;">No video uploaded</p>')
    video_preview.short_description = 'Video Preview'
    
    def document_preview(self, obj):
        if obj.document:
            return format_html(
                '<div style="margin-top: 10px;">'
                '<a href="{}" target="_blank" style="background: #2196F3; color: white; padding: 10px 20px; border-radius: 4px; text-decoration: none; display: inline-block;">📥 Download Document</a>'
                '</div>',
                obj.document.url
            )
        return format_html('<p style="color: #999;">No document uploaded</p>')
    document_preview.short_description = 'Document'
    
    @admin.action(description='📥 Export as CSV')
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="calculator_inquiries_{timestamp}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Category', 'Property Type', 'Floor', 'Location',
            'Flat/Society Name', 'Area (sqft)', 'Property Life (years)',
            'Owner Name', 'Phone Number', 'Additional Info', 'Created At'
        ])
        
        for inquiry in queryset:
            writer.writerow([
                inquiry.id,
                inquiry.get_title_display(),
                inquiry.property_type,
                inquiry.floor or '',
                inquiry.location,
                inquiry.flat_society_name,
                inquiry.area,
                inquiry.property_life,
                inquiry.owner_name,
                inquiry.phone_number,
                inquiry.additional_info or '',
                inquiry.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        self.message_user(request, f'{queryset.count()} inquiry(ies) exported successfully.')
        return response


# ============================================================================
# USER FAVORITE ADMIN
# ============================================================================

@admin.register(UserFavorite)
class UserFavoriteAdmin(admin.ModelAdmin):
    """Enhanced admin for User Favorites."""
    
    list_display = (
        'user_display',
        'property_display',
        'property_type_badge',
        'created_at'
    )
    
    list_filter = (
        'created_at',
        'property__property_type',
        'property__locations'
    )
    
    search_fields = (
        'user__email',
        'user__first_name',
        'user__last_name',
        'property__project_name'
    )
    
    fields = (
        'user',
        'property',
        'property_info',
        'created_at'
    )
    
    readonly_fields = ('property_info', 'created_at')
    
    ordering = ('-created_at',)
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    actions = ['export_as_csv']
    
    # Custom display methods
    
    def user_display(self, obj):
        return format_html(
            '<span style="font-weight: 500;">👤 {}</span>',
            obj.user.email
        )
    user_display.short_description = 'User'
    user_display.admin_order_field = 'user__email'
    
    def property_display(self, obj):
        return format_html(
            '<span style="font-weight: 500;">🏠 {}</span>',
            obj.property.project_name or 'Unnamed Property'
        )
    property_display.short_description = 'Property'
    property_display.admin_order_field = 'property__project_name'
    
    def property_type_badge(self, obj):
        color = '#4CAF50' if obj.property.property_type == 'residential' else '#2196F3'
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            color, obj.property.get_property_type_display()
        )
    property_type_badge.short_description = 'Type'
    
    def property_info(self, obj):
        return format_html(
            '<div style="margin-top: 10px; padding: 15px; background: #f5f5f5; border-radius: 8px;">'
            '<h4 style="margin-top: 0;">Property Details</h4>'
            '<p><strong>Project:</strong> {}</p>'
            '<p><strong>Type:</strong> {}</p>'
            '<p><strong>Category:</strong> {}</p>'
            '<p><strong>Location:</strong> {}</p>'
            '<p><strong>Area:</strong> {} sqft</p>'
            '</div>',
            obj.property.project_name or 'N/A',
            obj.property.get_property_type_display(),
            obj.property.get_category_display(),
            obj.property.locations.name if obj.property.locations else 'N/A',
            obj.property.area
        )
    property_info.short_description = 'Property Info'
    
    @admin.action(description='📥 Export as CSV')
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="user_favorites_{timestamp}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'User Email', 'Property Name', 'Property Type',
            'Property Category', 'Location', 'Added On'
        ])
        
        for favorite in queryset:
            writer.writerow([
                favorite.id,
                favorite.user.email,
                favorite.property.project_name or '',
                favorite.property.get_property_type_display(),
                favorite.property.get_category_display(),
                favorite.property.locations.name if favorite.property.locations else '',
                favorite.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        self.message_user(request, f'{queryset.count()} favorite(s) exported successfully.')
        return response
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'property', 'property__locations')
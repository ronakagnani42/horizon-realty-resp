from django.db import models
from django.core.validators import RegexValidator
from users.models import CustomUser
from django.utils import timezone
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
import os
from users.models import Newsletter
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.urls import reverse

'''
This module defines models for managing property listings and locations.

Models:
--------

1. PropertyLocation:
   - Represents a geographical location where properties are available.
   - Contains a single field 'name' to store the name of the property location.

2. BuyProperties:
   - Represents a property available for purchase, rental, or lease.
   - Contains fields for property type (residential/commercial), configuration (e.g., 1BHK, duplex), status (new, resale, rent, lease), and other property details.
   - Links to PropertyLocation to associate each property with a specific location.

Fields:
-------
- PropertyLocation:
   - 'name': The name of the property location (e.g., city, neighborhood, or area).
  
- BuyProperties:
   - 'property_type': The type of property (residential or commercial).
   - 'status': The property's current status (new, resale, rent, or lease).
   - 'configuration': The configuration for residential properties (e.g., 1BHK, duplex).
   - 'commercial_type': The type of commercial property (e.g., showroom, office).
   - 'furnishing': Indicates if the property is furnished or unfurnished.
   - 'area': The area of the property in square feet.
   - 'area_in_sqyards': The area of the property in square yards (optional).
   - 'budget': The budget for the property in INR.
   - 'locations': A foreign key relation to the PropertyLocation model to associate each property with a location.

This module provides a structured way to store and manage property listings and their associated locations.
'''

# Create your models here.

class PropertyLocation(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Property Location"
        verbose_name_plural = "Property Locations"


class NearbyPlaces(models.Model):
    DISTANCE_UNITS = [
        ('km', 'Kilometers'),
        ('m', 'Meters'),
    ]
    
    name = models.CharField(max_length=100, help_text="Name of the nearby amenity (e.g., Hospital, School, Metro)")
    distance_value = models.DecimalField(max_digits=8, decimal_places=2, help_text="Distance value")
    distance_unit = models.CharField(max_length=2, choices=DISTANCE_UNITS, default='km', help_text="Distance unit")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Nearby Place"
        verbose_name_plural = "Nearby Places"


class FeatureAmenity(models.Model):
    name = models.CharField(max_length=100, help_text="Name of the feature amenity (e.g., Swimming Pool, Gym)")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Feature Amenity"
        verbose_name_plural = "Feature Amenities"


class BuyProperties(models.Model):
    PROPERTY_TYPE_CHOICES = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
    ]
    RESIDENTIAL_CONFIG_CHOICES = [
        ('1bhk', '1BHK'),
        ('2bhk', '2BHK'),
        ('3bhk', '3BHK'),
        ('4bhk', '4BHK'),
        ('5bhk', '5BHK'),
        ('duplex', 'Duplex'),
        ('tenament', 'Tenament'),
        ('Bungalow', 'Bungalow'),
        ('villa', 'Villa'),
    ]
    COMMERCIAL_TYPE_CHOICES = [
        ('showroom', 'Showroom'),
        ('office', 'Office'),
        ('shop', 'Shop'),
        ('corporate_floors', 'Corporate Floors'),
    ]
    STATUS_CHOICES = [
        ('new', 'New'),
        ('resale', 'Resale'),
        ('rent', 'Rent'),
        ('lease', 'Lease'),
    ]
    PROPERTY_CATEGORY_CHOICES = [
        ('all', 'ALL'),
        ('leasing', 'LEASING'),
        ('investment', 'INVESTMENT'),
        ('resale_residential', 'RESALE RESIDENTIAL'),
    ]
    FURNISHING_CHOICES = [
        ('furnished', 'Furnished'),
        ('unfurnished', 'Unfurnished'),
    ]
    BUDGET_UNIT_CHOICES = [
        ('lakhs', 'Lakhs'),
        ('crores', 'Crores'),
    ]
    
    project_name = models.CharField(max_length=255, null=True, blank=True, unique=True)
    slug = models.SlugField(max_length=200, unique=True,blank=True)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, null=True, blank=True)
    category = models.CharField(max_length=20, choices=PROPERTY_CATEGORY_CHOICES, default='all')
    configuration = models.CharField(max_length=20, choices=RESIDENTIAL_CONFIG_CHOICES, blank=True, null=True)
    commercial_type = models.CharField(max_length=20, choices=COMMERCIAL_TYPE_CHOICES, blank=True, null=True)
    floor  = models.IntegerField(null=True, blank=True)
    rent_per_sqft = models.PositiveIntegerField(blank=True, null=True,help_text="On SBA")
    lockin_period = models.CharField(max_length=200,null=True, blank=True)
    increment = models.CharField(max_length=200,null=True, blank=True,help_text="In Percentage (%)")
    furnishing = models.CharField(max_length=20, choices=FURNISHING_CHOICES, blank=True, null=True)
    area = models.DecimalField(max_digits=10, decimal_places=2, help_text="Area in sqft")
    area_in_sqyards = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Area in square yards",
        blank=True,
        null=True
    )
    min_budget = models.DecimalField(max_digits=12,decimal_places=2, help_text="Minimum budget in INR",null=True, blank=True)
    min_budget_unit = models.CharField(
        max_length=10,
        choices=BUDGET_UNIT_CHOICES,
        default='lakhs',
        help_text="Unit for minimum budget"
    )
    max_budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_budget_unit = models.CharField(
        max_length=10,
        choices=BUDGET_UNIT_CHOICES,
        default='lakhs',
        help_text="Unit for maximum budget"
    )
    locations = models.ForeignKey(
        PropertyLocation,
        on_delete=models.CASCADE,
        null=True
    )
    image = models.ImageField(upload_to='property_images/', null=True, blank=True)
    brochure_pdf = models.FileField(
        upload_to='property_brochures/',
        null=True,
        blank=True,
        help_text="Upload a PDF brochure for this property"
    )
    possession_date = models.DateField(
        null=True, 
        blank=True,
        help_text="Expected or actual date of possession"
    )
    number_of_units = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Total number of units in the project"
    )
    number_of_lifts = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Number of lifts/elevators in the building"
    )
    number_of_storey = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Number of floors/storeys in the building"
    )
    salient_features = models.TextField(
        null=True, 
        blank=True,
        help_text="Key features of the property (comma-separated)"
    )
    nearby_amenities = models.ManyToManyField(
        'NearbyPlaces',
        blank=True,
        related_name='properties',
        help_text="Nearby amenities such as schools, hospitals, etc."
    )

    feature_amenities = models.ManyToManyField(
        'FeatureAmenity',
        blank=True,
        related_name='properties',
        help_text="Features like swimming pool, gym, clubhouse, etc."
    )
    is_property_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    def __str__(self):
        if self.project_name:
            min_budget_str = f"{self.min_budget} {self.min_budget_unit.capitalize()}"
            max_budget_str = f"{self.max_budget} {self.max_budget_unit.capitalize()}"
            return f"{self.project_name} - {self.property_type} - {self.area} sqft, {min_budget_str} to {max_budget_str}"
        return f"{self.property_type} - {self.area} sqft, {self.min_budget}-{self.max_budget}"

    def get_absolute_url(self):
        return reverse('property:property_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.pk or BuyProperties.objects.filter(pk=self.pk).exists() and BuyProperties.objects.get(pk=self.pk).project_name != self.project_name:
            self.slug = slugify(self.project_name)
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = "Buy Property"
        verbose_name_plural = "Buy Properties"

def validate_video_file(video):
    """
    Custom validator for video files
    """
    max_size = 50 * 1024 * 1024
    if video.size > max_size:
        raise ValidationError(f'Video file size cannot exceed 50 MB. Current size: {video.size / (1024 * 1024):.1f} MB')
    
    allowed_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.mkv', '.flv', '.webm']
    ext = os.path.splitext(video.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(f'Invalid video format. Allowed formats: {", ".join(allowed_extensions)}')
    
    return video

class SellResidentialProperties(models.Model):
    RESIDENTIAL_CONFIG_CHOICES = [
        ('1bhk', '1BHK'),
        ('2bhk', '2BHK'),
        ('3bhk', '3BHK'),
        ('4bhk', '4BHK'),
        ('5bhk', '5BHK'),
        ('duplex', 'Duplex'),
        ('tenament', 'Tenament'),
        ('Bungalow', 'Bungalow'),
        ('villa', 'Villa'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('resale', 'Resale'),
        ('rent', 'Rent'),
        ('lease', 'Lease'),
    ]
    PROPERTY_CATEGORY_CHOICES = [
        ('all', 'ALL'),
        ('leasing', 'LEASING'),
        ('investment', 'INVESTMENT'),
        ('resale_residential', 'RESALE RESIDENTIAL'),
    ]
    
    project_name = models.CharField(max_length=100, blank=False, null=False, help_text="Name of the project or building")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, null=True, blank=True)
    category = models.CharField(max_length=20, choices=PROPERTY_CATEGORY_CHOICES, default='all')
    configuration = models.CharField(max_length=20, choices=RESIDENTIAL_CONFIG_CHOICES, blank=True, null=True)
    area = models.DecimalField(max_digits=10, decimal_places=2, help_text="Area in sqft")
    area_in_sqyards = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Area in square yards",
        blank=True,
        null=True
    )
    budget = models.PositiveIntegerField(help_text="Budget in INR")
    floor_num = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Floor number of the commercial property"
    )
    unit_num = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Unit number or identifier (e.g., A-101, B-205)"
    )
    property_subtype = models.CharField(
    max_length=50,
    blank=True,
    null=True,
    help_text="Please specify the property type (required when 'Other' is selected)"
)
    locations = models.ForeignKey(
        PropertyLocation,
        on_delete=models.CASCADE,
        null=True
    )
    image = models.ImageField(upload_to='sell_residential_properties/', null=True, blank=True)
    video = models.FileField(
        upload_to='sell_residential_properties/videos/',
        null=True,
        blank=True,
        validators=[validate_video_file],
        help_text="Property video (max 50MB, formats: mp4, avi, mov, wmv, mkv, flv, webm)"
    )
    contact_email = models.EmailField(unique=False)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    contact_name = models.CharField(max_length=20, blank=True, null=True)
    additional_details = models.TextField(
        blank=True,
        null=True,
        help_text="Please mention any additional details related to rent, lease, lease increment, or specific requirements you'd like us to know"
    )
    is_approved = models.BooleanField(default=False, help_text="Admin approval status")

    def __str__(self):
        if self.project_name:
            return f"{self.project_name}  - {self.area} sqft, {self.budget} INR"
        return f"{self.project_name} - {self.area} sqft, {self.budget} INR"
    
    class Meta:
        verbose_name = "Sell Residential Property"
        verbose_name_plural = "Sell Residential Properties"

class SellCommercialProperties(models.Model):
    COMMERCIAL_TYPE_CHOICES = [
        ('showroom', 'Showroom'),
        ('office', 'Office'),
        ('shop', 'Shop'),
        ('corporate_floors', 'Corporate Floors'),
        ('other', 'Other'),

    ]
    STATUS_CHOICES = [
        ('resale', 'Resale'),
        ('rent', 'Rent'),
        ('lease', 'Lease'),
    ]
    FURNISHING_CHOICES = [
        ('furnished', 'Furnished'),
        ('semi-furnished', 'Semi-Furnished'),
        ('unfurnished', 'Unfurnished'),
    ]
    project_name = models.CharField(max_length=100, blank=False, null=False, help_text="Name of the project or building")
    commercial_type = models.CharField(max_length=20, choices=COMMERCIAL_TYPE_CHOICES, blank=True, null=True)
    furnishing = models.CharField(max_length=20, choices=FURNISHING_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, null=True, blank=True)
    area = models.DecimalField(max_digits=10, decimal_places=2, help_text="Area in sqft")
    area_in_sqyards = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Area in square yards",
        blank=True,
        null=True
    )
    budget = models.PositiveIntegerField(help_text="Budget in INR")
    locations = models.ForeignKey(
        PropertyLocation,
        on_delete=models.CASCADE,
        null=True
    )
    floor_num = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Floor number of the commercial property"
    )
    unit_num = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Unit number or identifier (e.g., A-101, B-205)"
    )
    property_subtype = models.CharField(
    max_length=50,
    blank=True,
    null=True,
    help_text="Please specify the property type (required when 'Other' is selected)"
)
    image = models.ImageField(upload_to='sell_commercial_properties/', null=True, blank=True)
    video = models.FileField(
        upload_to='sell_commercial_properties/videos/',
        null=True,
        blank=True,
        validators=[validate_video_file],
        help_text="Property video (max 50MB, formats: mp4, avi, mov, wmv, mkv, flv, webm)"
    )
    contact_email = models.EmailField(unique=False)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    contact_name = models.CharField(max_length=20, blank=True, null=True)
    additional_details = models.TextField(
        blank=True,
        null=True,
        help_text="Please mention any additional details related to rent, lease, lease increment, or specific requirements you'd like us to know"
    )
    is_approved = models.BooleanField(default=False, help_text="Admin approval status")

    def __str__(self):
        if self.project_name:
            return f"{self.project_name}  - {self.area} sqft, {self.budget} INR"
        return f"{self.project_name} - {self.area} sqft, {self.budget} INR"
    
    class Meta:
        verbose_name = "Sell Commercial Property"
        verbose_name_plural = "Sell Commercial Properties"

class InteriorDesignRequest(models.Model):
    """Model to store interior design service requests"""
    
    PROPERTY_TYPE_CHOICES = [
        ('flat', 'Flat'),
        ('bungalow', 'Bungalow'),
        ('penthouse', 'Penthouse'),
    ]
    
    SERVICE_TYPE_CHOICES = [
        ('turnkey', 'Turn key'),
        ('consultancy', 'Consultancy service'),
    ]
    
    name = models.CharField(
        max_length=100,
        verbose_name="Customer Name",
        help_text="Full name of the customer"
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        verbose_name="Phone Number",
        help_text="Contact phone number"
    )
    
    property_types = models.CharField(
        max_length=20,
        choices=PROPERTY_TYPE_CHOICES,
        verbose_name="Property Type",
        help_text="Select property type"
    )
    
    sqft = models.PositiveIntegerField(
        verbose_name="Square Feet (SBA)",
        help_text="Property area in square feet",
        null=True,
        blank=True
    )
    
    service_types = models.CharField(
        max_length=20,
        choices=SERVICE_TYPE_CHOICES,
        verbose_name="Service Type",
        help_text="Select service type"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )
    
    class Meta:
        verbose_name = "Interior Design Request"
        verbose_name_plural = "Interior Design Requests"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['phone_number']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_property_types_display()}"

class CheckOurWorkBrochure(models.Model):
    check_our_work_brochure = models.FileField(
        upload_to='check_our_work/',
        null=True,
        blank=True,
        help_text="Upload a PDF brochure to let users check your work"
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the brochure was uploaded"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this brochure is currently active/visible"
    )

    class Meta:
        verbose_name = "Check Our Work Brochure"
        verbose_name_plural = "Check Our Work Brochures"
        ordering = ['-uploaded_at']


    def get_file_name(self):
        if self.check_our_work_brochure:
            return self.check_our_work_brochure.name.split('/')[-1]
        return "No file uploaded"

    def get_file_size(self):
        if self.check_our_work_brochure:
            try:
                return f"{self.check_our_work_brochure.size / 1024:.1f} KB"
            except:
                return "Unknown size"
        return "No file"


class PropertyImage(models.Model):
    property = models.ForeignKey(BuyProperties, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='property_images/')
    caption = models.CharField(max_length=100, blank=True)
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Image for {self.property}"
    
    class Meta:
        ordering = ['-is_primary', 'id']

class PropertyVideo(models.Model):
    property = models.ForeignKey(BuyProperties, related_name='videos', on_delete=models.CASCADE)
    video = models.FileField(upload_to='property_videos/')
    thumbnail = models.ImageField(upload_to='video_thumbnails/', blank=True, null=True)
    title = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Video for {self.property}"

class PropertyInquiry(models.Model):
    property = models.ForeignKey(
        BuyProperties,
        on_delete=models.CASCADE,
        related_name='inquiries'
    )
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Inquiry from {self.name} about {self.property}"
    
    class Meta:
        verbose_name = "Property Inquiry"
        verbose_name_plural = "Property Inquiries"
        ordering = ['-created_at']


class PropertyCalculatorInquiry(models.Model):
    TITLE_CHOICES = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
    ]
    
    RESIDENTIAL_TYPE_CHOICES = [
        ('1bhk', '1 BHK'),
        ('2bhk', '2 BHK'),
        ('3bhk', '3 BHK'),
        ('4bhk', '4 BHK'),
        ('5bhk', '5 BHK'),
        ('duplex', 'Duplex'),
        ('tenament', 'Tenament'),
        ('bungalow', 'Bungalow'),
        ('villa', 'Villa'),
        ('other', 'Other'),
    ]
    
    COMMERCIAL_TYPE_CHOICES = [
        ('office', 'Office'),
        ('showroom', 'Showroom'),
        ('corporate floor', 'Corporate Floor'),
        ('shop', 'Shop'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=20, choices=TITLE_CHOICES, verbose_name="Property Category")
    property_type = models.CharField(max_length=20, verbose_name="Property Type")
    floor = models.IntegerField(verbose_name="Floor Number", null=True, blank=True)
    location = models.CharField(max_length=255, verbose_name="Location")
    flat_society_name = models.CharField(max_length=255, verbose_name="Flat/Society Name")
    area = models.PositiveIntegerField(verbose_name="Area (in sq ft)")
    property_life = models.PositiveIntegerField(verbose_name="Property Life (in years)")
    owner_name = models.CharField(max_length=255, verbose_name="Owner Name")
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, verbose_name="Phone Number")
    
    photo = models.ImageField(upload_to='property_inquiries/%Y/%m/%d/', verbose_name="Property Photo")
    video = models.FileField(upload_to='property_inquiries/%Y/%m/%d/', verbose_name="Property Video", null=True, blank=True)
    document = models.FileField(upload_to='property_inquiries/%Y/%m/%d/', verbose_name="Additional Document", null=True, blank=True)
    additional_info = models.TextField(verbose_name="Additional Information", null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.location}"
    
    class Meta:
        verbose_name = "Property Calculator Inquiry"
        verbose_name_plural = "Property Calculator Inquiries"
        ordering = ['-created_at']


class UserFavorite(models.Model):
    """Model to track user's favorite properties."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorites')
    property = models.ForeignKey('BuyProperties', on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "User Favorite"
        verbose_name_plural = "User Favorites"
        unique_together = ['user', 'property']
        
    def __str__(self):
        return f"{self.user.email}'s favorite: {self.property}"
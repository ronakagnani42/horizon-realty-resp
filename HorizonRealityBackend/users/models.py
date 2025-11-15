from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid


'''
This module defines a custom user model and manager for Django's authentication system.

CustomUserManager:
------------------
- This class defines custom manager methods for creating regular users and superusers.
- The `create_user` method ensures the email is provided, normalizes it, sets the password, and saves the user.
- The `create_superuser` method sets additional fields for superusers like `is_staff` and `is_superuser` and ensures they are set correctly.

CustomUser:
-----------
- This class extends Django's AbstractBaseUser and PermissionsMixin to implement a custom user model with email as the unique identifier.
- Custom user model features:
    - `email`: Unique email address for authentication (replaces username).
    - `contact_number`: Optional field to store the user's contact number.
    - `first_name`, `last_name`: Optional fields for storing user's personal information.
    - `is_active`: Boolean field to activate or deactivate the user.
    - `is_staff`: Determines whether the user has admin access.
    - `is_superuser`: Grants all permissions to the user.
    - `date_joined`: Automatically stores the date the user was created.
- The `USERNAME_FIELD` is set to `email`, which will be used for authentication.
- The `CustomUserManager` is set as the manager to handle user creation logic.

This custom model is ideal for projects where email is used as the primary identifier for users.

'''

class CustomUserManager(BaseUserManager):
    '''
        Creates and returns a regular user with an email and password.
    '''
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        '''
        Creates and returns a superuser with an email and password.
        '''
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    '''
    Custom User model that uses email as the primary authentication identifier.
    '''
    USER_TYPE_CHOICES = (
        ('', '---'),  #
        ('buyer', 'Buyer'),
        ('broker', 'Broker'),
    )
    FIRM_TYPE_CHOICES = (
        ('', '---'),  #
        ('individual', 'Individual'),
        ('firm', 'Firm'),
    )
    
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)

    # username = models.CharField(max_length=30, unique=True, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='')
    firm_type = models.CharField(max_length=10, choices=FIRM_TYPE_CHOICES, default='individual')
    firm_name = models.CharField(max_length=100, blank=True, null=True, help_text="Required for brokers only")
    is_broker = models.BooleanField(default=False)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False, help_text="Grants access to admin features.")
    is_superuser = models.BooleanField(default=False, help_text="Grants all permissions without assigning them explicitly.")
    date_joined = models.DateTimeField(auto_now_add=True)
    newsletter_subscribed = models.BooleanField(default=False, help_text="User subscribed to newsletter")
    last_profile_update = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Timestamp of the last profile update"
    )
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
    
    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        self.is_broker = (self.user_type == 'broker')
        super().save(*args, **kwargs)

class Newsletter(models.Model):
    STATUS_CHOICES = (
        ('subscribed', 'Subscribed'),
        ('unsubscribed', 'Unsubscribed'),
        ('pending', 'Pending Confirmation'),
    )
    
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='subscribed')
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    unsubscribe_token = models.UUIDField(default=uuid.uuid4, unique=True)
    source = models.CharField(max_length=50, default='registration')
    
    class Meta:
        verbose_name = "Newsletter Subscription"
        verbose_name_plural = "Newsletter Subscriptions"
        
    def __str__(self):
        return f"{self.email} - {self.status}"
    
    def unsubscribe(self):
        """Method to unsubscribe user"""
        self.status = 'unsubscribed'
        self.unsubscribed_at = timezone.now()
        self.save()
        
    @classmethod
    def subscribe_email(cls, email, name=None, source='registration'):
        """Class method to subscribe an email"""
        newsletter, created = cls.objects.get_or_create(
            email=email,
            defaults={
                'name': name,
                'status': 'subscribed',
                'source': source
            }
        )
        
        if not created and newsletter.status == 'unsubscribed':
            newsletter.status = 'subscribed'
            newsletter.subscribed_at = timezone.now()
            newsletter.unsubscribed_at = None
            newsletter.save()
            
        return newsletter, created

class ContactSubmission(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"

    class Meta:
        verbose_name = "Contact Submission"
        verbose_name_plural = "Contact Submissions"

class ContactInformation(models.Model):
    """
    Model to store company contact information including address, phone numbers,
    email addresses, and office hours.
    """
    office_name = models.CharField(max_length=100, default="Our Office")
    street_address = models.CharField(max_length=255)
    area = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    primary_phone = models.CharField(validators=[phone_regex], max_length=17)
    secondary_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    
    primary_email = models.EmailField()
    secondary_email = models.EmailField(blank=True, null=True)
    
    weekday_hours_start = models.TimeField()
    weekday_hours_end = models.TimeField()
    saturday_hours_start = models.TimeField(blank=True, null=True)
    saturday_hours_end = models.TimeField(blank=True, null=True)
    sunday_hours_start = models.TimeField(blank=True, null=True)
    sunday_hours_end = models.TimeField(blank=True, null=True)
    
    is_main_office = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.office_name} - {self.city}, {self.state}"
    
    def get_full_address(self):
        """Returns the complete formatted address"""
        return f"{self.street_address}, {self.area}, {self.city}, {self.state} {self.postal_code}, {self.country}"
    
    def get_weekday_hours(self):
        """Returns formatted weekday office hours"""
        return f"{self.weekday_hours_start.strftime('%I:%M %p')} - {self.weekday_hours_end.strftime('%I:%M %p')}"
    
    class Meta:
        verbose_name = "Contact Information"
        verbose_name_plural = "Contact Information"
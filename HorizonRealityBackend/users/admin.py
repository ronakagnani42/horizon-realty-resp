from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser,ContactSubmission, ContactInformation, Newsletter

'''
This module defines customizations for the Django admin interface for the CustomUser model.

CustomUserAdmin:
----------------
- This class customizes the display and behavior of the CustomUser model in the Django admin interface.
- It extends the default UserAdmin class to include additional fields such as 'contact_number', 'user_type'
  and customizes the layout of fields for adding and editing users.

Fields and Configuration:
-------------------------
- list_display: Specifies the fields displayed in the user list view, including first name, last name, 
  email, contact number, user type, and permissions (staff, superuser, active status).
- search_fields: Allows searching users by email, first name, last name, or contact number.
- readonly_fields: Displays 'date_joined' and 'last_login' as read-only fields.
- fieldsets: Defines the sections of fields displayed in the user edit form, such as personal info, 
  permissions, and important dates.
- add_fieldsets: Customizes the fields shown when creating a new user, including email, password, 
  contact number, user type, and permissions.

This customization enhances the user management interface for admins by making it more intuitive 
and including additional user attributes.
'''

class CustomUserAdmin(BaseUserAdmin):
    list_display = ('first_name', 'last_name', 'email', 'contact_number', 'user_type','firm_type', 'is_broker', 'is_verified','firm_name', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'contact_number', 'firm_name')
    readonly_fields = ('date_joined', 'last_login', 'is_broker','is_verified','newsletter_subscribed')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'contact_number', 'user_type','firm_type', 'firm_name')}),
        (_('Status'), {'fields': ('is_broker',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions', 'groups')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'contact_number', 'user_type', 'firm_name','firm_type', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )
    ordering = ('email',)

class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'submitted_at')
    search_fields = ('name', 'email', 'subject')
    readonly_fields = ('submitted_at',)

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'status', 'source', 'subscribed_at', 'unsubscribed_at')
    list_filter = ('status', 'source', 'subscribed_at')
    search_fields = ('email', 'name')
    readonly_fields = ('subscribed_at', 'unsubscribed_at', 'unsubscribe_token')
    ordering = ('-subscribed_at',)
    fieldsets = (
        (None, {
            'fields': ('email', 'name', 'status', 'source')
        }),
        ('Timestamps', {
            'fields': ('subscribed_at', 'unsubscribed_at'),
        }),
        ('Tokens', {
            'fields': ('unsubscribe_token',),
        }),
    )

@admin.register(ContactInformation)
class ContactInformationAdmin(admin.ModelAdmin):
    list_display = ('office_name', 'city', 'primary_phone', 'primary_email', 'is_main_office', 'last_updated')
    list_filter = ('is_main_office', 'city', 'state')
    search_fields = ('office_name', 'street_address', 'city', 'primary_phone', 'primary_email')
    fieldsets = (
        ('Office Information', {
            'fields': ('office_name', 'is_main_office')
        }),
        ('Address', {
            'fields': ('street_address', 'area', 'city', 'state', 'postal_code', 'country')
        }),
        ('Contact Details', {
            'fields': ('primary_phone', 'secondary_phone', 'primary_email', 'secondary_email')
        }),
        ('Office Hours', {
            'fields': (
                ('weekday_hours_start', 'weekday_hours_end'),
                ('saturday_hours_start', 'saturday_hours_end'),
                ('sunday_hours_start', 'sunday_hours_end')
            )
        })
    )
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ContactSubmission, ContactSubmissionAdmin)
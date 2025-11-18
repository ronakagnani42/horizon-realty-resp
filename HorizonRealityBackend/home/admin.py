from .models import AboutUs,TeamMember,Statistics, Testimonial, Service, ServiceImage
from django.utils.html import format_html, mark_safe
from django.contrib import admin

'''
This module contains custom admin configurations for managing the following models:
- AboutUs
- TeamMember
- ContactSubmission
- Statistics
- Testimonial
- Service

Custom Admin Configurations:
----------------------------

1. AboutUsAdmin:
   - Displays shortened versions of welcome text, mission, and vision on the list page.
   - Adds custom fieldsets for structured display of content related to the introduction, team, mission, vision, and achievements.
   - Limits the ability to add a new "About Us" entry to only one instance of the model.

2. TeamMemberAdmin:
   - Displays team member names and designations.
   - Enables filtering and searching by designation for easy management of team data.

3. StatisticsAdmin:
   - Lists company statistics (happy clients, projects, hours of support, hard workers).
   - Allows editable fields for projects, hours of support, and hard workers for easy updates in the admin interface.

4. TestimonialAdmin:
   - Displays client testimonial data, including name, designation, rating, and creation timestamp.
   - Includes search functionality to quickly locate testimonials by name or designation.

5. ServiceAdmin:
   - Displays key information about the service, including title, description, and icon.
   - Renders icons as Bootstrap icons using the `render_icon` method.
   - Limits description to a shortened version (first 50 characters) in the list display.
   - Pre-populates the slug field based on the service title for SEO-friendly URLs.
   - Customizes the display of icons in the list view and allows upload of static and dynamic icons.

Permissions:
-------------
- The `AboutUsAdmin` limits the ability to add a new "About Us" entry, ensuring that only one instance exists in the database at any time.

Each model is registered with the admin site, using the custom configurations above to improve usability and content management.
'''

class AboutUsAdmin(admin.ModelAdmin):
    list_display = ('short_welcome_text', 'short_mission', 'short_vision', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = (
        'welcome_text', 'mission_statement', 'vision_statement',
        'team_member_1_name', 'team_member_2_name'
    )

    fields = [
        'welcome_text',
        'introduction_video',

        'team_photo',
        'team_description',

        'team_member_1_name',
        'team_member_1_designation',
        'team_member_1_description',
        'team_member_1_photo',

        'team_member_2_name',
        'team_member_2_designation',
        'team_member_2_description',
        'team_member_2_photo',

        'mission_statement',
        'vision_statement',

        'achievement_title_1',
        'achievement_description_1',
        'achievement_photo_1',

        'achievement_title_2',
        'achievement_description_2',
        'achievement_photo_2',
    ]
    
    def short_welcome_text(self, obj):
        return self._shorten_text(obj.welcome_text)
    short_welcome_text.short_description = 'Welcome Text'
    
    def short_mission(self, obj):
        return self._shorten_text(obj.mission_statement)
    short_mission.short_description = 'Mission'
    
    def short_vision(self, obj):
        return self._shorten_text(obj.vision_statement)
    short_vision.short_description = 'Vision'
    
    def _shorten_text(self, text, length=50):
        if text and len(text) > length:
            return format_html(
                '<span title="{}">{}...</span>',
                text, text[:length]
            )
        return text
    
    
    def has_add_permission(self, request):
        return not AboutUs.objects.exists()

class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'designation')
    search_fields = ('name', 'designation')  
    list_filter = ('designation',)  

@admin.register(Statistics)
class StatisticsAdmin(admin.ModelAdmin):
    list_display = ('happy_clients', 'projects', 'hours_of_support', 'hard_workers','is_stats_active')
    list_editable = ('projects', 'hours_of_support', 'hard_workers') 
    list_display_links = ('happy_clients',) 
    
    def has_add_permission(self, request):
        # If one instance exists, disable the Add button
        if Statistics.objects.exists():
            return False
        return True

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'designation', 'created_at','is_testimonial_active')
    search_fields = ('name', 'designation')


class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 1
    fields = ('image', 'title', 'is_featured', 'order')

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'short_description', 'static_icon', 'render_icon', 'phone_number', 'image_count','is_service_active')
    search_fields = ('title', 'description', 'detail', 'phone_number')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ServiceImageInline]

    def short_description(self, obj):
        return (obj.description[:50] + '...') if len(obj.description) > 50 else obj.description
    short_description.short_description = 'Description'

    def render_icon(self, obj):
        """ Render the Bootstrap icon in the admin list view. """
        if obj.icon:
            return mark_safe(f'<i class="bi {obj.icon}"></i>')
        return "No Icon"
    render_icon.short_description = 'Icon'
    
    def image_count(self, obj):
        """Display the number of images associated with this service."""
        count = obj.images.count()
        return count
    image_count.short_description = 'Images'

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'detail', 'phone_number','is_service_active')
        }),
        ('Icons', {
            'fields': ('static_icon', 'icon'),
            'classes': ('collapse',)
        }),
    )



admin.site.register(AboutUs, AboutUsAdmin)
admin.site.register(TeamMember, TeamMemberAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceImage)
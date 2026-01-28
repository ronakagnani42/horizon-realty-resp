from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.urls import reverse
from django.http import HttpResponse
import csv
from datetime import datetime
from .models import AboutUs, TeamMember, Statistics, Testimonial, Service, ServiceImage


# ============================================================================
# SERVICE IMAGE INLINE
# ============================================================================

class ServiceImageInline(admin.TabularInline):
    """
    Inline admin for managing service images directly within the Service admin page.
    """
    model = ServiceImage
    extra = 1
    min_num = 0
    fields = ('image_preview', 'image', 'title', 'is_featured', 'order')
    readonly_fields = ('image_preview',)
    classes = ('collapse',)
    
    def image_preview(self, obj):
        """Display a preview of the image."""
        if obj.image:
            return format_html(
                '<img src="{}" width="80" height="80" style="object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">No image</span>')
    image_preview.short_description = 'Preview'


# ============================================================================
# ABOUT US ADMIN
# ============================================================================

@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    """
    Enhanced admin interface for AboutUs model.
    """
    
    list_display = (
        'welcome_text_preview',
        'mission_preview',
        'vision_preview',
        'team_members_badge',
        'achievements_badge',
        'updated_at'
    )
    
    list_filter = ('updated_at',)
    
    search_fields = (
        'welcome_text',
        'mission_statement',
        'vision_statement',
        'team_member_1_name',
        'team_member_2_name'
    )
    
    fields = (
        'welcome_text',
        'introduction_video',
        'team_photo',
        'team_photo_preview',
        'team_description',
        'team_member_1_name',
        'team_member_1_designation',
        'team_member_1_description',
        'team_member_1_photo',
        'team_member_1_photo_preview',
        'team_member_2_name',
        'team_member_2_designation',
        'team_member_2_description',
        'team_member_2_photo',
        'team_member_2_photo_preview',
        'mission_statement',
        'vision_statement',
        'achievement_title_1',
        'achievement_description_1',
        'achievement_photo_1',
        'achievement_photo_1_preview',
        'achievement_title_2',
        'achievement_description_2',
        'achievement_photo_2',
        'achievement_photo_2_preview',
    )
    
    readonly_fields = (
        'team_photo_preview',
        'team_member_1_photo_preview',
        'team_member_2_photo_preview',
        'achievement_photo_1_preview',
        'achievement_photo_2_preview'
    )
    
    actions = ['export_as_csv']
    
    # Custom display methods
    
    def welcome_text_preview(self, obj):
        """Display shortened welcome text."""
        return self._format_text_preview(obj.welcome_text, 60)
    welcome_text_preview.short_description = 'Welcome Text'
    
    def mission_preview(self, obj):
        """Display shortened mission statement."""
        return self._format_text_preview(obj.mission_statement, 50)
    mission_preview.short_description = 'Mission'
    
    def vision_preview(self, obj):
        """Display shortened vision statement."""
        return self._format_text_preview(obj.vision_statement, 50)
    vision_preview.short_description = 'Vision'
    
    def team_members_badge(self, obj):
        """Display team members count badge."""
        count = sum([1 for name in [obj.team_member_1_name, obj.team_member_2_name] if name])
        if count > 0:
            return format_html(
                '<span style="background: #2196F3; color: white; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">👥 {} members</span>',
                count
            )
        return format_html('<span style="color: #999;">No members</span>')
    team_members_badge.short_description = 'Team Members'
    
    def achievements_badge(self, obj):
        """Display achievements count badge."""
        count = sum([1 for title in [obj.achievement_title_1, obj.achievement_title_2] if title])
        if count > 0:
            return format_html(
                '<span style="background: #FF9800; color: white; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">🏆 {} achievements</span>',
                count
            )
        return format_html('<span style="color: #999;">No achievements</span>')
    achievements_badge.short_description = 'Achievements'
    
    # Image preview methods
    
    def team_photo_preview(self, obj):
        """Display team photo preview."""
        return self._get_image_preview(obj.team_photo, 'Team Photo')
    team_photo_preview.short_description = 'Team Photo Preview'
    
    def team_member_1_photo_preview(self, obj):
        """Display team member 1 photo preview."""
        return self._get_image_preview(obj.team_member_1_photo, 'Team Member 1 Photo')
    team_member_1_photo_preview.short_description = 'Photo Preview'
    
    def team_member_2_photo_preview(self, obj):
        """Display team member 2 photo preview."""
        return self._get_image_preview(obj.team_member_2_photo, 'Team Member 2 Photo')
    team_member_2_photo_preview.short_description = 'Photo Preview'
    
    def achievement_photo_1_preview(self, obj):
        """Display achievement 1 photo preview."""
        return self._get_image_preview(obj.achievement_photo_1, 'Achievement 1 Photo')
    achievement_photo_1_preview.short_description = 'Photo Preview'
    
    def achievement_photo_2_preview(self, obj):
        """Display achievement 2 photo preview."""
        return self._get_image_preview(obj.achievement_photo_2, 'Achievement 2 Photo')
    achievement_photo_2_preview.short_description = 'Photo Preview'
    
    # Helper methods
    
    def _format_text_preview(self, text, length=50):
        """Format text with preview and tooltip."""
        if text and len(text) > length:
            return format_html(
                '<span style="cursor: help;" title="{}">{}<span style="color: #999;">...</span></span>',
                text, text[:length]
            )
        return text or format_html('<span style="color: #999;">Empty</span>')
    
    def _get_image_preview(self, image_field, alt_text):
        """Generate image preview HTML."""
        if image_field:
            return format_html(
                '<div style="margin-top: 10px;">'
                '<img src="{}" alt="{}" style="max-width: 400px; max-height: 300px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" />'
                '</div>',
                image_field.url, alt_text
            )
        return format_html('<p style="color: #999;">No image uploaded</p>')
    
    # Actions
    
    @admin.action(description='📥 Export as CSV')
    def export_as_csv(self, request, queryset):
        """Export AboutUs data to CSV."""
        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="aboutus_export_{timestamp}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Welcome Text', 'Mission', 'Vision',
            'Team Member 1', 'Team Member 1 Designation',
            'Team Member 2', 'Team Member 2 Designation',
            'Achievement 1', 'Achievement 2', 'Updated At'
        ])
        
        for obj in queryset:
            writer.writerow([
                obj.id,
                obj.welcome_text or '',
                obj.mission_statement or '',
                obj.vision_statement or '',
                obj.team_member_1_name or '',
                obj.team_member_1_designation or '',
                obj.team_member_2_name or '',
                obj.team_member_2_designation or '',
                obj.achievement_title_1 or '',
                obj.achievement_title_2 or '',
                obj.updated_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(obj, 'updated_at') else ''
            ])
        
        self.message_user(request, f'{queryset.count()} record(s) exported successfully.')
        return response
    
    # Permissions
    
    def has_add_permission(self, request):
        """Limit to one AboutUs instance."""
        return not AboutUs.objects.exists()
    
    class Media:
        css = {
            'all': ('admin/css/custom_blog_admin.css',)
        }


# ============================================================================
# TEAM MEMBER ADMIN
# ============================================================================

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    """
    Enhanced admin interface for TeamMember model.
    """
    
    list_display = (
        'name_with_icon',
        'designation_badge',
        'photo_preview',
        'description_preview',
        'social_links_count'
    )
    
    list_filter = ('designation',)
    search_fields = ('name', 'designation', 'description')
    
    fields = (
        'name',
        'designation',
        'description',
        'photo',
        'photo_display',
        'linkedin_url',
        'twitter_url',
        'facebook_url',
        'instagram_url'
    )
    
    readonly_fields = ('photo_display',)
    
    ordering = ('name',)
    list_per_page = 25
    
    actions = ['duplicate_members', 'export_as_csv']
    
    # Custom display methods
    
    def name_with_icon(self, obj):
        """Display name with icon."""
        return format_html(
            '<span style="font-weight: 500;">👤 {}</span>',
            obj.name
        )
    name_with_icon.short_description = 'Name'
    name_with_icon.admin_order_field = 'name'
    
    def designation_badge(self, obj):
        """Display designation as badge."""
        return format_html(
            '<span style="background: #673AB7; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            obj.designation
        )
    designation_badge.short_description = 'Designation'
    designation_badge.admin_order_field = 'designation'
    
    def photo_preview(self, obj):
        """Display photo thumbnail."""
        if obj.photo:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 50%; border: 2px solid #673AB7;" />',
                obj.photo.url
            )
        return format_html(
            '<div style="width: 50px; height: 50px; background: #f0f0f0; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #999; font-size: 20px;">👤</div>'
        )
    photo_preview.short_description = 'Photo'
    
    def photo_display(self, obj):
        """Display larger photo in detail view."""
        if obj.photo:
            return format_html(
                '<div style="margin-top: 10px;">'
                '<img src="{}" style="max-width: 300px; max-height: 300px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" />'
                '</div>',
                obj.photo.url
            )
        return format_html('<p style="color: #999;">No photo uploaded</p>')
    photo_display.short_description = 'Current Photo'
    
    def description_preview(self, obj):
        """Display shortened description."""
        if obj.description and len(obj.description) > 60:
            return format_html(
                '<span title="{}">{}<span style="color: #999;">...</span></span>',
                obj.description, obj.description[:60]
            )
        return obj.description or format_html('<span style="color: #999;">No description</span>')
    description_preview.short_description = 'Description'
    
    def social_links_count(self, obj):
        """Display count of social media links."""
        links = [obj.linkedin_url, obj.twitter_url, obj.facebook_url, obj.instagram_url]
        count = sum(1 for link in links if link)
        if count > 0:
            return format_html(
                '<span style="background: #00BCD4; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">🔗 {} links</span>',
                count
            )
        return format_html('<span style="color: #999;">No links</span>')
    social_links_count.short_description = 'Social Links'
    
    # Actions
    
    @admin.action(description='📋 Duplicate selected members')
    def duplicate_members(self, request, queryset):
        """Duplicate selected team members."""
        duplicated_count = 0
        for member in queryset:
            member.pk = None
            member.name = f"{member.name} (Copy)"
            member.save()
            duplicated_count += 1
        
        self.message_user(request, f'{duplicated_count} member(s) duplicated successfully.')
    
    @admin.action(description='📥 Export as CSV')
    def export_as_csv(self, request, queryset):
        """Export team members to CSV."""
        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="team_members_export_{timestamp}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Name', 'Designation', 'Description',
            'Photo URL', 'LinkedIn', 'Twitter', 'Facebook', 'Instagram'
        ])
        
        for member in queryset:
            writer.writerow([
                member.id,
                member.name,
                member.designation,
                member.description or '',
                member.photo.url if member.photo else '',
                member.linkedin_url or '',
                member.twitter_url or '',
                member.facebook_url or '',
                member.instagram_url or ''
            ])
        
        self.message_user(request, f'{queryset.count()} member(s) exported successfully.')
        return response
    
    class Media:
        css = {
            'all': ('admin/css/custom_blog_admin.css',)
        }


# ============================================================================
# STATISTICS ADMIN
# ============================================================================

@admin.register(Statistics)
class StatisticsAdmin(admin.ModelAdmin):
    """
    Enhanced admin interface for Statistics model.
    """
    
    list_display = (
        'stats_overview',
        'happy_clients_badge',
        'projects_badge',
        'support_hours_badge',
        'workers_badge',
        'status_badge'
    )
    
    
    fields = (
        'happy_clients',
        'projects',
        'hours_of_support',
        'hard_workers',
        'is_stats_active'
    )
    
    actions = ['activate_stats', 'deactivate_stats', 'duplicate_stats', 'export_as_csv']
    
    # Custom display methods
    
    def stats_overview(self, obj):
        """Display overall statistics overview."""
        return format_html(
            '<div style="font-weight: 600; font-size: 13px;">📊 Statistics Overview</div>'
        )
    stats_overview.short_description = 'Overview'
    
    def happy_clients_badge(self, obj):
        """Display happy clients count."""
        return format_html(
            '<div style="text-align: center;">'
            '<div style="background: #4CAF50; color: white; padding: 8px 12px; border-radius: 8px; font-weight: 600; display: inline-block;">'
            '<div style="font-size: 20px;">{}</div>'
            '<div style="font-size: 10px; opacity: 0.9;">😊 CLIENTS</div>'
            '</div></div>',
            obj.happy_clients
        )
    happy_clients_badge.short_description = 'Happy Clients'
    
    def projects_badge(self, obj):
        """Display projects count."""
        return format_html(
            '<div style="text-align: center;">'
            '<div style="background: #2196F3; color: white; padding: 8px 12px; border-radius: 8px; font-weight: 600; display: inline-block;">'
            '<div style="font-size: 20px;">{}</div>'
            '<div style="font-size: 10px; opacity: 0.9;">📁 PROJECTS</div>'
            '</div></div>',
            obj.projects
        )
    projects_badge.short_description = 'Projects'
    
    def support_hours_badge(self, obj):
        """Display support hours count."""
        return format_html(
            '<div style="text-align: center;">'
            '<div style="background: #FF9800; color: white; padding: 8px 12px; border-radius: 8px; font-weight: 600; display: inline-block;">'
            '<div style="font-size: 20px;">{}</div>'
            '<div style="font-size: 10px; opacity: 0.9;">⏰ HOURS</div>'
            '</div></div>',
            obj.hours_of_support
        )
    support_hours_badge.short_description = 'Support Hours'
    
    def workers_badge(self, obj):
        """Display hard workers count."""
        return format_html(
            '<div style="text-align: center;">'
            '<div style="background: #9C27B0; color: white; padding: 8px 12px; border-radius: 8px; font-weight: 600; display: inline-block;">'
            '<div style="font-size: 20px;">{}</div>'
            '<div style="font-size: 10px; opacity: 0.9;">👷 WORKERS</div>'
            '</div></div>',
            obj.hard_workers
        )
    workers_badge.short_description = 'Hard Workers'
    
    def status_badge(self, obj):
        """Display active status."""
        if hasattr(obj, 'is_stats_active'):
            if obj.is_stats_active:
                return format_html(
                    '<span style="background: #4CAF50; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">✓ Active</span>'
                )
            return format_html(
                '<span style="background: #f44336; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">✗ Inactive</span>'
            )
        return '-'
    status_badge.short_description = 'Status'
    
    # Actions
    
    @admin.action(description='✓ Activate statistics')
    def activate_stats(self, request, queryset):
        """Activate selected statistics."""
        if hasattr(Statistics, 'is_stats_active'):
            updated = queryset.update(is_stats_active=True)
            self.message_user(request, f'{updated} statistic(s) activated.')
        else:
            self.message_user(request, 'This model does not have is_stats_active field.', level='warning')
    
    @admin.action(description='✗ Deactivate statistics')
    def deactivate_stats(self, request, queryset):
        """Deactivate selected statistics."""
        if hasattr(Statistics, 'is_stats_active'):
            updated = queryset.update(is_stats_active=False)
            self.message_user(request, f'{updated} statistic(s) deactivated.')
        else:
            self.message_user(request, 'This model does not have is_stats_active field.', level='warning')
    
    @admin.action(description='📋 Duplicate selected statistics')
    def duplicate_stats(self, request, queryset):
        """Duplicate selected statistics."""
        duplicated_count = 0
        for stat in queryset:
            stat.pk = None
            if hasattr(stat, 'is_stats_active'):
                stat.is_stats_active = False
            stat.save()
            duplicated_count += 1
        
        self.message_user(request, f'{duplicated_count} statistic(s) duplicated successfully.')
    
    @admin.action(description='📥 Export as CSV')
    def export_as_csv(self, request, queryset):
        """Export statistics to CSV."""
        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="statistics_export_{timestamp}.csv"'
        
        writer = csv.writer(response)
        headers = ['ID', 'Happy Clients', 'Projects', 'Hours of Support', 'Hard Workers']
        if hasattr(Statistics, 'is_stats_active'):
            headers.append('Is Active')
        writer.writerow(headers)
        
        for stat in queryset:
            row = [
                stat.id,
                stat.happy_clients,
                stat.projects,
                stat.hours_of_support,
                stat.hard_workers
            ]
            if hasattr(stat, 'is_stats_active'):
                row.append('Yes' if stat.is_stats_active else 'No')
            writer.writerow(row)
        
        self.message_user(request, f'{queryset.count()} statistic(s) exported successfully.')
        return response
    
    # Permissions
    
    def has_add_permission(self, request):
        """Limit to one Statistics instance."""
        return not Statistics.objects.exists()
    
    class Media:
        css = {
            'all': ('admin/css/custom_blog_admin.css',)
        }


# ============================================================================
# TESTIMONIAL ADMIN
# ============================================================================

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    """
    Enhanced admin interface for Testimonial model.
    """
    
    list_display = (
        'name_with_icon',
        'designation_badge',
        'status_badge',
        'created_at'
    )
    
    list_filter = ('created_at',)
    if 'is_testimonial_active' in [f.name for f in Testimonial._meta.get_fields()]:
        list_filter = ('is_testimonial_active', 'created_at')
    
    search_fields = ('name', 'designation', 'feedback')
    
    fields = (
        'name',
        'designation',
        'photo',
        'photo_display',
        'is_testimonial_active',
        'created_at'
    )
    
    readonly_fields = ('photo_display', 'created_at')
    
    ordering = ('-created_at',)
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    actions = ['activate_testimonials', 'deactivate_testimonials', 'duplicate_testimonials', 'export_as_csv']
    
    # Custom display methods
    
    def name_with_icon(self, obj):
        """Display name with icon."""
        return format_html(
            '<span style="font-weight: 500;">💬 {}</span>',
            obj.name
        )
    name_with_icon.short_description = 'Name'
    name_with_icon.admin_order_field = 'name'
    
    def designation_badge(self, obj):
        """Display designation as badge."""
        return format_html(
            '<span style="background: #00BCD4; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            obj.designation
        )
    designation_badge.short_description = 'Designation'
    designation_badge.admin_order_field = 'designation'
    
    def rating_stars(self, obj):
        """Display rating as stars."""
        if hasattr(obj, 'rating'):
            stars = '⭐' * int(obj.rating)
            empty_stars = '☆' * (5 - int(obj.rating))
            return format_html(
                '<span style="font-size: 16px; letter-spacing: 2px;">{}{}</span>',
                stars, empty_stars
            )
        return '-'
    rating_stars.short_description = 'Rating'
    rating_stars.admin_order_field = 'rating' if hasattr(Testimonial, 'rating') else None
    
    def feedback_preview(self, obj):
        """Display shortened feedback."""
        if obj.feedback and len(obj.feedback) > 80:
            return format_html(
                '<span style="font-style: italic;" title="{}">{}<span style="color: #999;">...</span></span>',
                obj.feedback, obj.feedback[:80]
            )
        return format_html('<span style="font-style: italic;">{}</span>', obj.feedback) if obj.feedback else format_html('<span style="color: #999;">No feedback</span>')
    feedback_preview.short_description = 'Feedback'
    
    def status_badge(self, obj):
        """Display active status."""
        if hasattr(obj, 'is_testimonial_active'):
            if obj.is_testimonial_active:
                return format_html(
                    '<span style="background: #4CAF50; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">✓ Active</span>'
                )
            return format_html(
                '<span style="background: #f44336; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">✗ Inactive</span>'
            )
        return '-'
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'is_testimonial_active' if hasattr(Testimonial, 'is_testimonial_active') else None
    
    def photo_display(self, obj):
        """Display photo in detail view."""
        if hasattr(obj, 'photo') and obj.photo:
            return format_html(
                '<div style="margin-top: 10px;">'
                '<img src="{}" style="max-width: 200px; max-height: 200px; border-radius: 50%; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" />'
                '</div>',
                obj.photo.url
            )
        return format_html('<p style="color: #999;">No photo uploaded</p>')
    photo_display.short_description = 'Current Photo'
    
    # Actions
    
    @admin.action(description='✓ Activate testimonials')
    def activate_testimonials(self, request, queryset):
        """Activate selected testimonials."""
        if hasattr(Testimonial, 'is_testimonial_active'):
            updated = queryset.update(is_testimonial_active=True)
            self.message_user(request, f'{updated} testimonial(s) activated.')
        else:
            self.message_user(request, 'This model does not have is_testimonial_active field.', level='warning')
    
    @admin.action(description='✗ Deactivate testimonials')
    def deactivate_testimonials(self, request, queryset):
        """Deactivate selected testimonials."""
        if hasattr(Testimonial, 'is_testimonial_active'):
            updated = queryset.update(is_testimonial_active=False)
            self.message_user(request, f'{updated} testimonial(s) deactivated.')
        else:
            self.message_user(request, 'This model does not have is_testimonial_active field.', level='warning')
    
    @admin.action(description='📋 Duplicate selected testimonials')
    def duplicate_testimonials(self, request, queryset):
        """Duplicate selected testimonials."""
        duplicated_count = 0
        for testimonial in queryset:
            testimonial.pk = None
            if hasattr(testimonial, 'is_testimonial_active'):
                testimonial.is_testimonial_active = False
            testimonial.save()
            duplicated_count += 1
        
        self.message_user(request, f'{duplicated_count} testimonial(s) duplicated successfully.')
    
    @admin.action(description='📥 Export as CSV')
    def export_as_csv(self, request, queryset):
        """Export testimonials to CSV."""
        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="testimonials_export_{timestamp}.csv"'
        
        writer = csv.writer(response)
        headers = ['ID', 'Name', 'Designation', 'Feedback']
        if hasattr(Testimonial, 'rating'):
            headers.append('Rating')
        if hasattr(Testimonial, 'photo'):
            headers.append('Photo URL')
        if hasattr(Testimonial, 'is_testimonial_active'):
            headers.append('Is Active')
        headers.append('Created At')
        writer.writerow(headers)
        
        for testimonial in queryset:
            row = [
                testimonial.id,
                testimonial.name,
                testimonial.designation,
                testimonial.feedback or ''
            ]
            if hasattr(testimonial, 'rating'):
                row.append(testimonial.rating)
            if hasattr(testimonial, 'photo'):
                row.append(testimonial.photo.url if testimonial.photo else '')
            if hasattr(testimonial, 'is_testimonial_active'):
                row.append('Yes' if testimonial.is_testimonial_active else 'No')
            row.append(testimonial.created_at.strftime('%Y-%m-%d %H:%M:%S'))
            writer.writerow(row)
        
        self.message_user(request, f'{queryset.count()} testimonial(s) exported successfully.')
        return response
    
    class Media:
        css = {
            'all': ('admin/css/custom_blog_admin.css',)
        }


# ============================================================================
# SERVICE ADMIN
# ============================================================================

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """
    Enhanced admin interface for Service model.
    """
    
    list_display = (
        'title_with_icon',
        'slug_display',
        'description_preview',
        'icon_display',
        'phone_display',
        'image_count_badge',
        'status_badge'
    )
    
    list_filter = ()
    if 'is_service_active' in [f.name for f in Service._meta.get_fields()]:
        list_filter = ('is_service_active',)
    
    search_fields = ('title', 'description', 'detail', 'phone_number', 'slug')
    
    fields = (
        'title',
        'slug',
        'description',
        'detail',
        'phone_number',
        'static_icon',
        'static_icon_preview',
        'icon',
        'is_service_active'
    )
    
    readonly_fields = ('static_icon_preview',)
    prepopulated_fields = {'slug': ('title',)}
    
    inlines = [ServiceImageInline]
    
    ordering = ('title',)
    list_per_page = 25
    
    actions = ['activate_services', 'deactivate_services', 'duplicate_services', 'export_as_csv']
    
    # Custom display methods
    
    def title_with_icon(self, obj):
        """Display title with icon."""
        return format_html(
            '<span style="font-weight: 500;">🔧 {}</span>',
            obj.title
        )
    title_with_icon.short_description = 'Title'
    title_with_icon.admin_order_field = 'title'
    
    def slug_display(self, obj):
        """Display slug with monospace font."""
        return format_html(
            '<code style="background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</code>',
            obj.slug
        )
    slug_display.short_description = 'Slug'
    slug_display.admin_order_field = 'slug'
    
    def description_preview(self, obj):
        """Display shortened description."""
        if obj.description and len(obj.description) > 60:
            return format_html(
                '<span title="{}">{}<span style="color: #999;">...</span></span>',
                obj.description, obj.description[:60]
            )
        return obj.description or format_html('<span style="color: #999;">No description</span>')
    description_preview.short_description = 'Description'
    
    def icon_display(self, obj):
        """Display Bootstrap icon."""
        if obj.icon:
            return format_html(
                '<i class="bi {}" style="font-size: 24px; color: #2196F3;"></i>',
                obj.icon
            )
        return format_html('<span style="color: #999;">No icon</span>')
    icon_display.short_description = 'Icon'
    
    def static_icon_preview(self, obj):
        """Display static icon preview."""
        if hasattr(obj, 'static_icon') and obj.static_icon:
            return format_html(
                '<div style="margin-top: 10px;">'
                '<img src="{}" style="max-width: 100px; max-height: 100px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" />'
                '</div>',
                obj.static_icon.url
            )
        return format_html('<p style="color: #999;">No static icon uploaded</p>')
    static_icon_preview.short_description = 'Static Icon Preview'
    
    def phone_display(self, obj):
        """Display phone number."""
        if obj.phone_number:
            return format_html(
                '<a href="tel:{}" style="color: #4CAF50; text-decoration: none; font-weight: 500;">📞 {}</a>',
                obj.phone_number, obj.phone_number
            )
        return format_html('<span style="color: #999;">No phone</span>')
    phone_display.short_description = 'Phone'
    phone_display.admin_order_field = 'phone_number'
    
    def image_count_badge(self, obj):
        """Display count of service images."""
        count = obj.images.count()
        if count > 0:
            return format_html(
                '<span style="background: #FF9800; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">📸 {} images</span>',
                count
            )
        return format_html(
            '<span style="background: #e0e0e0; color: #666; padding: 3px 8px; border-radius: 12px; font-size: 11px;">0 images</span>'
        )
    image_count_badge.short_description = 'Gallery'
    
    def status_badge(self, obj):
        """Display active status."""
        if hasattr(obj, 'is_service_active'):
            if obj.is_service_active:
                return format_html(
                    '<span style="background: #4CAF50; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">✓ Active</span>'
                )
            return format_html(
                '<span style="background: #f44336; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">✗ Inactive</span>'
            )
        return '-'
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'is_service_active' if hasattr(Service, 'is_service_active') else None
    
    # Actions
    
    @admin.action(description='✓ Activate services')
    def activate_services(self, request, queryset):
        """Activate selected services."""
        if hasattr(Service, 'is_service_active'):
            updated = queryset.update(is_service_active=True)
            self.message_user(request, f'{updated} service(s) activated.')
        else:
            self.message_user(request, 'This model does not have is_service_active field.', level='warning')
    
    @admin.action(description='✗ Deactivate services')
    def deactivate_services(self, request, queryset):
        """Deactivate selected services."""
        if hasattr(Service, 'is_service_active'):
            updated = queryset.update(is_service_active=False)
            self.message_user(request, f'{updated} service(s) deactivated.')
        else:
            self.message_user(request, 'This model does not have is_service_active field.', level='warning')
    
    @admin.action(description='📋 Duplicate selected services')
    def duplicate_services(self, request, queryset):
        """Duplicate selected services."""
        duplicated_count = 0
        for service in queryset:
            # Store original images
            original_images = list(service.images.all())
            
            # Duplicate service
            service.pk = None
            service.title = f"{service.title} (Copy)"
            service.slug = None  # Will be auto-generated
            if hasattr(service, 'is_service_active'):
                service.is_service_active = False
            service.save()
            
            # Duplicate images
            for img in original_images:
                img.pk = None
                img.service = service
                img.save()
            
            duplicated_count += 1
        
        self.message_user(request, f'{duplicated_count} service(s) duplicated successfully.')
    
    @admin.action(description='📥 Export as CSV')
    def export_as_csv(self, request, queryset):
        """Export services to CSV."""
        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="services_export_{timestamp}.csv"'
        
        writer = csv.writer(response)
        headers = ['ID', 'Title', 'Slug', 'Description', 'Detail', 'Phone Number', 'Icon', 'Images Count']
        if hasattr(Service, 'static_icon'):
            headers.append('Static Icon URL')
        if hasattr(Service, 'is_service_active'):
            headers.append('Is Active')
        writer.writerow(headers)
        
        for service in queryset:
            row = [
                service.id,
                service.title,
                service.slug,
                service.description or '',
                service.detail or '',
                service.phone_number or '',
                service.icon or '',
                service.images.count()
            ]
            if hasattr(service, 'static_icon'):
                row.append(service.static_icon.url if service.static_icon else '')
            if hasattr(service, 'is_service_active'):
                row.append('Yes' if service.is_service_active else 'No')
            writer.writerow(row)
        
        self.message_user(request, f'{queryset.count()} service(s) exported successfully.')
        return response
    
    # Override get methods for better control
    
    def get_queryset(self, request):
        """Optimize queryset with prefetch for image count."""
        qs = super().get_queryset(request)
        return qs.annotate(image_count=Count('images'))
    
    class Media:
        css = {
            'all': ('admin/css/custom_blog_admin.css',)
        }


# ============================================================================
# SERVICE IMAGE ADMIN
# ============================================================================

@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    """
    Standalone admin interface for ServiceImage model.
    """
    
    list_display = (
        'image_preview_thumbnail',
        'service_title',
        'title_display',
        'featured_badge',
        'order_badge',
    )
    
    list_filter = ('is_featured', 'service__is_service_active') if hasattr(Service, 'is_service_active') else ('is_featured',)
    search_fields = ('service__title', 'title')
    
    fields = (
        'service',
        'image',
        'large_image_preview',
        'title',
        'is_featured',
        'order'
    )
    
    readonly_fields = ('large_image_preview',)
    
    ordering = ('service', 'order')
    list_per_page = 30
    
    actions = ['make_featured', 'remove_featured', 'duplicate_images', 'export_as_csv']
    
    # Custom display methods
    
    def image_preview_thumbnail(self, obj):
        """Display small thumbnail in list view."""
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 4px; border: 2px solid #2196F3;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">No image</span>')
    image_preview_thumbnail.short_description = 'Preview'
    
    def large_image_preview(self, obj):
        """Display larger preview in detail view."""
        if obj.image:
            return format_html(
                '<div style="margin-top: 10px;">'
                '<img src="{}" style="max-width: 500px; max-height: 400px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" />'
                '</div>',
                obj.image.url
            )
        return format_html('<p style="color: #999;">No image uploaded</p>')
    large_image_preview.short_description = 'Image Preview'
    
    def service_title(self, obj):
        """Display the associated service title."""
        return format_html(
            '<span style="font-weight: 500;">🔧 {}</span>',
            obj.service.title
        )
    service_title.short_description = 'Service'
    service_title.admin_order_field = 'service__title'
    
    def title_display(self, obj):
        """Display image title."""
        if obj.title:
            return format_html('<span style="font-style: italic;">{}</span>', obj.title[:50])
        return format_html('<span style="color: #999;">No title</span>')
    title_display.short_description = 'Title'
    
    def featured_badge(self, obj):
        """Display featured status."""
        if obj.is_featured:
            return format_html(
                '<span style="background: #FFD700; color: #333; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">⭐ Featured</span>'
            )
        return format_html('<span style="color: #999;">-</span>')
    featured_badge.short_description = 'Featured'
    featured_badge.admin_order_field = 'is_featured'
    
    def order_badge(self, obj):
        """Display order number."""
        return format_html(
            '<span style="background: #9C27B0; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">#{}</span>',
            obj.order
        )
    order_badge.short_description = 'Order'
    order_badge.admin_order_field = 'order'
    
  
    
    # Actions
    
    @admin.action(description='⭐ Make featured')
    def make_featured(self, request, queryset):
        """Make selected images featured."""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} image(s) marked as featured.')
    
    @admin.action(description='Remove featured')
    def remove_featured(self, request, queryset):
        """Remove featured status from selected images."""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} image(s) removed from featured.')
    
    @admin.action(description='📋 Duplicate selected images')
    def duplicate_images(self, request, queryset):
        """Duplicate selected service images."""
        duplicated_count = 0
        for img in queryset:
            img.pk = None
            img.is_featured = False
            img.save()
            duplicated_count += 1
        
        self.message_user(request, f'{duplicated_count} image(s) duplicated successfully.')
    
    @admin.action(description='📥 Export as CSV')
    def export_as_csv(self, request, queryset):
        """Export service images to CSV."""
        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="service_images_export_{timestamp}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Service ID', 'Service Title', 'Image URL',
            'Title', 'Is Featured', 'Order'
        ])
        
        for img in queryset:
            writer.writerow([
                img.id,
                img.service.id,
                img.service.title,
                img.image.url if img.image else '',
                img.title or '',
                'Yes' if img.is_featured else 'No',
                img.order
            ])
        
        self.message_user(request, f'{queryset.count()} image(s) exported successfully.')
        return response
    
    class Media:
        css = {
            'all': ('admin/css/custom_blog_admin.css',)
        }
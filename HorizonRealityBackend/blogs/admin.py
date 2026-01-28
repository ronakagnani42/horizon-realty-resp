from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.urls import reverse
from django.http import HttpResponse
import csv
from datetime import datetime
from .models import Blog, BlogImage


class BlogImageInline(admin.TabularInline):
    """
    Inline admin for managing blog images directly within the Blog admin page.
    Provides a clean tabular interface with image previews.
    """
    model = BlogImage
    extra = 1
    min_num = 0
    fields = ('image_preview', 'image', 'caption', 'description')
    readonly_fields = ('image_preview',)
    classes = ('collapse',)  # Makes the inline collapsible
    
    def image_preview(self, obj):
        """Display a medium-sized preview of the image."""
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">No image</span>')
    image_preview.short_description = 'Preview'


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    """
    Enhanced admin interface for Blog model with improved UI and functionality.
    """
    
    # List display configuration
    list_display = (
        'title_with_icon',
        'slug_display',
        'main_image_preview',
        'image_count',
        'visibility_badge',
        'blog_link_button',
        'created_at',
        'updated_at'
    )
    
    # List configuration
    list_filter = (
        'is_visible',
        'created_at',
        'updated_at',
    )
    
    search_fields = ('title', 'description', 'slug')
    
    # Simple field listing without fieldsets
    fields = (
        'title',
        'slug',
        'description',
        'image',
        'main_image_display',
        'link',
        'is_visible',
        'created_at',
        'updated_at'
    )
    
    readonly_fields = ('created_at', 'updated_at', 'main_image_display')
    prepopulated_fields = {'slug': ('title',)}
    
    # Inline configuration
    inlines = [BlogImageInline]
    
    # Ordering and pagination
    ordering = ('-created_at',)
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    # Actions
    actions = ['make_visible', 'make_hidden', 'duplicate_blog', 'export_as_csv']
    
    # Custom display methods
    
    def title_with_icon(self, obj):
        """Display title with a blog icon."""
        icon = '📝'
        return format_html(
            '<span style="font-weight: 500;">{} {}</span>',
            icon, obj.title
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
    
    def main_image_preview(self, obj):
        """Display a thumbnail preview of the main blog image."""
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return format_html(
            '<div style="width: 60px; height: 60px; background: #f0f0f0; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: #999; font-size: 11px;">No Image</div>'
        )
    main_image_preview.short_description = 'Image'
    
    def main_image_display(self, obj):
        """Display a larger preview of the main image in the detail view."""
        if obj.image:
            return format_html(
                '<div style="margin-top: 10px;">'
                '<img src="{}" style="max-width: 400px; max-height: 300px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" />'
                '</div>',
                obj.image.url
            )
        return format_html('<p style="color: #999;">No image uploaded</p>')
    main_image_display.short_description = 'Current Image'
    
    def image_count(self, obj):
        """Display count of additional images."""
        count = obj.images.count()
        if count > 0:
            return format_html(
                '<span style="background: #4CAF50; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">{} images</span>',
                count
            )
        return format_html(
            '<span style="background: #e0e0e0; color: #666; padding: 3px 8px; border-radius: 12px; font-size: 11px;">0 images</span>'
        )
    image_count.short_description = 'Gallery'
    
    def visibility_badge(self, obj):
        """Display visibility status as a colored badge."""
        if obj.is_visible:
            return format_html(
                '<span style="background: #4CAF50; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">✓ Visible</span>'
            )
        return format_html(
            '<span style="background: #f44336; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">✗ Hidden</span>'
        )
    visibility_badge.short_description = 'Status'
    visibility_badge.admin_order_field = 'is_visible'
    
    def blog_link_button(self, obj):
        """Display a styled button linking to the blog."""
        if obj.link:
            return format_html(
                '<a href="{}" target="_blank" style="background: #2196F3; color: white; padding: 5px 12px; border-radius: 4px; text-decoration: none; font-size: 11px; font-weight: 600; display: inline-block;">🔗 View Blog</a>',
                obj.link
            )
        return format_html(
            '<span style="color: #999; font-size: 11px;">No link</span>'
        )
    blog_link_button.short_description = 'External Link'
    
    # Custom actions
    
    @admin.action(description='✓ Make selected blogs visible')
    def make_visible(self, request, queryset):
        """Bulk action to make blogs visible."""
        updated = queryset.update(is_visible=True)
        self.message_user(request, f'{updated} blog(s) marked as visible.')
    
    @admin.action(description='✗ Make selected blogs hidden')
    def make_hidden(self, request, queryset):
        """Bulk action to hide blogs."""
        updated = queryset.update(is_visible=False)
        self.message_user(request, f'{updated} blog(s) marked as hidden.')
    
    @admin.action(description='📋 Duplicate selected blogs')
    def duplicate_blog(self, request, queryset):
        """Duplicate selected blogs with a 'Copy' suffix."""
        duplicated_count = 0
        for blog in queryset:
            # Store original images
            original_images = list(blog.images.all())
            
            # Duplicate blog
            blog.pk = None
            blog.title = f"{blog.title} (Copy)"
            blog.slug = None  # Will be auto-generated
            blog.is_visible = False
            blog.save()
            
            # Duplicate images
            for img in original_images:
                img.pk = None
                img.blog = blog
                img.save()
            
            duplicated_count += 1
        
        self.message_user(request, f'{duplicated_count} blog(s) duplicated successfully.')
    
    @admin.action(description='📥 Export selected blogs as CSV')
    def export_as_csv(self, request, queryset):
        """Export selected blogs to CSV file."""
        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="blogs_export_{timestamp}.csv"'
        
        # Create CSV writer
        writer = csv.writer(response)
        
        # Write header row
        writer.writerow([
            'ID',
            'Title',
            'Slug',
            'Description',
            'Image URL',
            'External Link',
            'Is Visible',
            'Gallery Images Count',
            'Created At',
            'Updated At'
        ])
        
        # Write data rows
        for blog in queryset:
            writer.writerow([
                blog.id,
                blog.title,
                blog.slug,
                blog.description or '',
                blog.image.url if blog.image else '',
                blog.link or '',
                'Yes' if blog.is_visible else 'No',
                blog.images.count(),
                blog.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                blog.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        self.message_user(request, f'{queryset.count()} blog(s) exported successfully.')
        return response
    
    # Override get methods for better control
    
    def get_queryset(self, request):
        """Optimize queryset with prefetch for image count."""
        qs = super().get_queryset(request)
        return qs.annotate(image_count=Count('images'))
    
    class Media:
        """Add custom CSS for better admin styling."""
        css = {
            'all': ('admin/css/custom_blog_admin.css',)  # Optional: create this file for additional styling
        }


@admin.register(BlogImage)
class BlogImageAdmin(admin.ModelAdmin):
    """
    Standalone admin interface for BlogImage with enhanced preview capabilities.
    """
    
    list_display = (
        'image_preview_thumbnail',
        'blog_title',
        'caption_display',
        'has_description',
        'admin_link_to_blog'
    )
    
    list_filter = ('blog__is_visible',)
    search_fields = ('blog__title', 'caption', 'description')
    
    # Simple field listing without fieldsets
    fields = (
        'blog',
        'image',
        'large_image_preview',
        'caption',
        'description'
    )
    
    readonly_fields = ('large_image_preview',)
    
    ordering = ('-id',)
    list_per_page = 30
    
    # Actions
    actions = ['export_as_csv']
    
    def image_preview_thumbnail(self, obj):
        """Display small thumbnail in list view."""
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />',
                obj.image.url
            )
        return '-'
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
        return 'No image'
    large_image_preview.short_description = 'Image Preview'
    
    def blog_title(self, obj):
        """Display the associated blog title."""
        return obj.blog.title
    blog_title.short_description = 'Blog'
    blog_title.admin_order_field = 'blog__title'
    
    def caption_display(self, obj):
        """Display caption or placeholder."""
        if obj.caption:
            return format_html('<span style="font-style: italic;">{}</span>', obj.caption[:50])
        return format_html('<span style="color: #999;">No caption</span>')
    caption_display.short_description = 'Caption'
    
    def has_description(self, obj):
        """Show if description exists."""
        if obj.description:
            return format_html('✓')
        return format_html('<span style="color: #ccc;">-</span>')
    has_description.short_description = 'Description'
    has_description.admin_order_field = 'description'
    
    def admin_link_to_blog(self, obj):
        """Link to parent blog admin page."""
        url = reverse('admin:blogs_blog_change', args=[obj.blog.pk])
        return format_html(
            '<a href="{}" style="color: #2196F3; text-decoration: none;">→ Edit Blog</a>',
            url
        )
    admin_link_to_blog.short_description = 'Actions'
    
    @admin.action(description='📥 Export selected images as CSV')
    def export_as_csv(self, request, queryset):
        """Export selected blog images to CSV file."""
        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="blog_images_export_{timestamp}.csv"'
        
        # Create CSV writer
        writer = csv.writer(response)
        
        # Write header row
        writer.writerow([
            'ID',
            'Blog ID',
            'Blog Title',
            'Image URL',
            'Caption',
            'Description',
            'Blog Visible'
        ])
        
        # Write data rows
        for img in queryset:
            writer.writerow([
                img.id,
                img.blog.id,
                img.blog.title,
                img.image.url if img.image else '',
                img.caption or '',
                img.description or '',
                'Yes' if img.blog.is_visible else 'No'
            ])
        
        self.message_user(request, f'{queryset.count()} image(s) exported successfully.')
        return response
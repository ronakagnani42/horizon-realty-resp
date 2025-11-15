from django.utils.html import format_html
from .models import Blog, BlogImage
from django.contrib import admin

'''
This module customizes the Django admin interface for managing Blog and BlogImage models.

Admin Features:
----------------

1. BlogImageInline:
   - Allows inline editing of BlogImage instances directly within a Blog's admin page.
   - Displays a small thumbnail of each image.
   - `image` and `image_thumbnail` are marked as readonly to avoid accidental changes.

   Fields:
   - image_thumbnail: A small preview of the image (readonly).
   - image: The actual image file (readonly in inline).
   - caption: Optional caption text for each image.

2. BlogAdmin:
   - Enhances the Blog admin interface with the following:
     - List display includes blog title, link, main image thumbnail, visibility, and timestamps.
     - Inline display of associated BlogImage instances using BlogImageInline.
     - Clickable link to the external blog URL.
     - Readonly timestamps and image field upon editing an existing blog.

   Features:
   - blog_link: Renders a clickable "View Blog" link in the admin.
   - image_thumbnail: Shows a thumbnail preview of the main blog image.
   - get_readonly_fields: Conditionally makes the image field readonly if already set.

Admin Registration:
--------------------
- Blog is registered using the custom BlogAdmin class.
- BlogImage is registered normally to allow independent access if needed.

These admin enhancements improve usability and visual management of blogs and their related images.
'''


class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'blog_link', 'image_thumbnail', 'is_visible', 'created_at', 'updated_at')
    list_filter = ('is_visible', 'created_at', 'updated_at')
    search_fields = ('title',)
    readonly_fields = ('created_at', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-created_at',)

    def blog_link(self, obj):
        """Display a clickable link to the blog."""
        return format_html('<a href="{}" target="_blank">View Blog</a>', obj.link)
    blog_link.short_description = 'Blog Link'

    def image_thumbnail(self, obj):
        """Display a small thumbnail for the main image."""
        if obj.image and obj.image.url:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                obj.image.url
            )
        return "-"
    image_thumbnail.short_description = 'Main Image'

    def get_readonly_fields(self, request, obj=None):
        """Make the image field readonly when editing."""
        if obj and obj.image:
            return self.readonly_fields + ('image',)
        return self.readonly_fields

admin.site.register(Blog, BlogAdmin)
admin.site.register(BlogImage)

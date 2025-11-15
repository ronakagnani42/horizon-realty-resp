from django.db import models
from django.urls import reverse
from django.utils.text import slugify
# Create your models here.
'''
This module defines the data models for a blogging feature in a Django application.

Models:
--------

1. Blog:
   - Represents a blog entry with a title, image, optional external link, description, and visibility status.
   - Includes timestamps for when the blog was created and last updated.
   - Has a Boolean field `is_visible` to control the display of the blog on the frontend.

   Fields:
   - title: The main heading of the blog.
   - image: A featured image for the blog.
   - link: An optional URL to an external resource.
   - description: A short description or excerpt from the blog.
   - created_at: Automatically set to the time the blog is created.
   - updated_at: Automatically set to the time the blog is last updated.
   - is_visible: A flag to control whether the blog is shown publicly.

2. BlogImage:
   - Represents additional images related to a blog.
   - Each image is linked to a specific blog via a ForeignKey relationship.

   Fields:
   - blog: ForeignKey linking to the associated Blog.
   - image: The image file itself.
   - caption: An optional short caption for the image.
   - description: An optional detailed description of the image.

The models are set up with verbose names for better readability in the Django admin interface.
'''


class Blog(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='blogs/', null=True, blank=True)
    link = models.URLField(blank=True, null=True)
    description = models.TextField(max_length=500, blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)     
    is_visible = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blogs:blog_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.pk or Blog.objects.filter(pk=self.pk).exists() and Blog.objects.get(pk=self.pk).title != self.title:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Blog"
        verbose_name_plural = "Blogs"


class BlogImage(models.Model):
    blog = models.ForeignKey(Blog, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='blog_images/',null=True, blank=True)
    caption = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(max_length=1000, blank=True, null=True)
    
    def __str__(self):
        return f"Image for {self.blog.title} - {self.caption}"

    class Meta:
        verbose_name = "Blog Image"
        verbose_name_plural = "Blog Images"
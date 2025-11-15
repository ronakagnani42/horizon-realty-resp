from django.utils.text import slugify
from django.urls import reverse
from django.db import models

'''
This module defines the core models for the About Us, Team, Contact, Statistics, Testimonials, and Services sections
of a Django-based website. These models are used to manage and display dynamic content on corresponding frontend pages.

Models:
--------

1. AboutUs:
   - Stores introductory content, media, and company achievements.
   - Includes optional fields for team photo, video, and descriptions.
   - Provides a method to convert a YouTube video URL into an embeddable format.

2. TeamMember:
   - Represents individual members of the team.
   - Stores their name, designation, and profile picture.

3. ContactSubmission:
   - Handles user-submitted contact form data.
   - Includes name, email, subject, message, and timestamp of submission.

4. Statistics:
   - Displays key performance or company metrics such as number of happy clients, projects, support hours, and workers.
   - Intended for visual counters or infographics on the frontend.

5. Testimonial:
   - Represents client testimonials including name, photo, rating, and text.
   - Used to display client feedback on the website.

6. Service:
   - Represents individual services offered by the company.
   - Includes slug for clean URLs, icon uploads, detailed descriptions, and optional phone contact.
   - Automatically updates slug based on title changes using Django's `slugify`.

Meta:
------
- All models include verbose names for better readability in the Django admin interface.
- Some models include timestamps (`created_at`, `updated_at`) for tracking.

Helper Methods:
----------------
- `AboutUs.get_embed_video_url()`: Converts a YouTube URL to an embeddable format.
- `Service.get_absolute_url()`: Returns a URL pattern name for dynamic linking in templates.
- `Service.save()`: Automatically generates a slug from the service title when saving.

This module enables full backend management of informational and promotional website content.
'''


class AboutUs(models.Model):
    welcome_text = models.TextField(help_text="Introduction text for the About Us section")
    team_photo = models.ImageField(upload_to='about_us/', blank=True, null=True, help_text="Common team photo")
    team_member_1_name = models.CharField(max_length=255, blank=True, null=True, help_text="Name of team member 1")
    team_member_1_designation = models.CharField(max_length=255, blank=True, null=True, help_text="Designation of team member 1")
    team_member_1_description = models.TextField(blank=True, null=True, help_text="Description of team member 1")
    team_member_1_photo = models.ImageField(upload_to='about_us/team/', blank=True, null=True, help_text="Photo of team member 1")
    team_member_2_name = models.CharField(max_length=255, blank=True, null=True, help_text="Name of team member 2")
    team_member_2_designation = models.CharField(max_length=255, blank=True, null=True, help_text="Designation of team member 2")
    team_member_2_description = models.TextField(blank=True, null=True, help_text="Description of team member 2")
    team_member_2_photo = models.ImageField(upload_to='about_us/team/', blank=True, null=True, help_text="Photo of team member 2")
    team_description = models.TextField(help_text="Description of the team", null=True, blank=True)
    introduction_video = models.URLField(blank=True, null=True, help_text="URL of the introductory video")
    mission_statement = models.TextField(help_text="Company mission statement")
    vision_statement = models.TextField(help_text="Company vision statement")
    achievement_title_1 = models.CharField(max_length=255, blank=True, null=True, help_text="Title of achievement 1")
    achievement_description_1 = models.TextField(blank=True, null=True, help_text="Description of achievement 1")
    achievement_photo_1 = models.ImageField(upload_to='about_us/achievements/', blank=True, null=True, help_text="Photo for achievement 1")
    achievement_title_2 = models.CharField(max_length=255, blank=True, null=True, help_text="Title of achievement 2")
    achievement_description_2 = models.TextField(blank=True, null=True, help_text="Description of achievement 2")
    achievement_photo_2 = models.ImageField(upload_to='about_us/achievements/', blank=True, null=True, help_text="Photo for achievement 2")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "About Us Content"

    def get_embed_video_url(self):
        if self.introduction_video:
            if "watch?v=" in self.introduction_video:
                return self.introduction_video.replace("watch?v=", "embed/")
            elif "youtu.be/" in self.introduction_video:
                video_id = self.introduction_video.split("youtu.be/")[1]
                return f"https://www.youtube.com/embed/{video_id}"
        return None

    class Meta:
        verbose_name = "About Us"
        verbose_name_plural = "About Us"


class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100) 
    profile_picture = models.ImageField(upload_to='team/')

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"



class Statistics(models.Model):
    happy_clients = models.PositiveIntegerField(default=0)
    projects = models.PositiveIntegerField(default=0)
    hours_of_support = models.PositiveIntegerField(default=0)
    hard_workers = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "Statistics"

    class Meta:
        verbose_name = "Statistic"
        verbose_name_plural = "Statistics"


class Testimonial(models.Model):
    name = models.CharField(max_length=255, help_text="Name of the client")
    designation = models.CharField(max_length=255, blank=True, null=True, help_text="Client's designation (e.g., CEO, Designer)")
    text = models.TextField(help_text="Testimonial content")
    photo = models.ImageField(upload_to='testimonials/', blank=True, null=True, help_text="Photo of the client")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_testimonial_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"

class Service(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.ImageField(upload_to='services/', blank=True, null=True)
    static_icon = models.ImageField(upload_to='static_services/', blank=True, null=True)
    description = models.TextField()
    detail = models.TextField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_service_active = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('service_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.pk or Service.objects.get(pk=self.pk).title != self.title:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class ServiceImage(models.Model):
    """Model for storing multiple images for a service."""
    service = models.ForeignKey('Service', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='service_images/')
    title = models.CharField(max_length=100, blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Service Image'
        verbose_name_plural = 'Service Images'
    
    def __str__(self):
        return f"{self.service.title} - {self.title if self.title else 'Image'}"
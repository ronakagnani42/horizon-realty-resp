
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from services.models import SellResidentialProperties, SellCommercialProperties


@receiver(pre_save, sender=SellResidentialProperties)
def store_previous_approval_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._previous_approval_status = SellResidentialProperties.objects.get(pk=instance.pk).is_approved
        except SellResidentialProperties.DoesNotExist:
            instance._previous_approval_status = False
    else:
        instance._previous_approval_status = False

@receiver(post_save, sender=SellResidentialProperties)
def send_approval_email(sender, instance, created, **kwargs):
    """Send email when property gets approved"""
    
    if not created and hasattr(instance, '_previous_approval_status'):
        if not instance._previous_approval_status and instance.is_approved:
            
            try:
                subject = f"Property Approved: {instance.project_name}"
                
                context = {
                    'contact_name': instance.contact_name or 'Dear Customer',
                    'project_name': instance.project_name,
                    'configuration': instance.get_configuration_display() if instance.configuration else 'N/A',
                    'area': instance.area,
                    'budget': instance.budget,
                    'status': instance.get_status_display() if instance.status else 'N/A',
                    'location': instance.locations.name if instance.locations else 'N/A',
                }
                
                html_message = render_to_string('emails/property_approved.html', context)
                plain_message = strip_tags(html_message)
                
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.contact_email],
                    html_message=html_message,
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Failed to send approval email to {instance.contact_email}: {str(e)}")



@receiver(pre_save, sender=SellCommercialProperties)
def store_previous_approval_status(sender, instance, **kwargs):
    """Store the previous approval status before saving"""
    if instance.pk:
        try:
            instance._previous_approval_status = SellCommercialProperties.objects.get(pk=instance.pk).is_approved
        except SellCommercialProperties.DoesNotExist:
            instance._previous_approval_status = False
    else:
        instance._previous_approval_status = False


@receiver(post_save, sender=SellCommercialProperties)
def send_approval_email(sender, instance, created, **kwargs):
    """Send email when property gets approved"""
    
    if not created and hasattr(instance, '_previous_approval_status'):
        if not instance._previous_approval_status and instance.is_approved:
            
            try:
                subject = f"Property Approved: {instance.project_name}"
                
                context = {
                    'contact_name': instance.contact_name or 'Dear Customer',
                    'project_name': instance.project_name,
                    'area': instance.area,
                    'budget': instance.budget,
                    'status': instance.get_status_display() if instance.status else 'N/A',
                    'location': instance.locations.name if instance.locations else 'N/A',
                }
                
                html_message = render_to_string('emails/commercial_property_approved.html', context)
                plain_message = strip_tags(html_message)
                
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.contact_email],
                    html_message=html_message,
                    fail_silently=False,
                )                
            except Exception as e:
                print(f"Failed to send approval email to {instance.contact_email}: {str(e)}")

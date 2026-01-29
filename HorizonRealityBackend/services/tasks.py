from celery import shared_task 
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Newsletter, BuyProperties, CustomUser
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_verification_email_task(self, user_id, verification_url, domain):
    """
    Send verification email asynchronously with retry logic.
    Retries up to 3 times with 60 second delay between attempts.
    
    Args:
        user_id: ID of the user to send verification email to
        verification_url: URL for email verification
        domain: Current site domain
    """
    try:
        user = CustomUser.objects.get(pk=user_id)
        
        subject = 'Verify Your Horizon Reality Account'
        html_message = render_to_string('emails/verification_email.html', {
            'user': user,
            'verification_url': verification_url,
            'domain': domain,
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Verification email sent successfully to {user.email}")
        return f"Verification email sent successfully to {user.email}"
    
    except CustomUser.DoesNotExist:
        logger.error(f"User with ID {user_id} not found")
        return f"User with ID {user_id} not found"
    
    except Exception as exc:
        logger.warning(f"Error sending verification email to user {user_id}: {str(exc)}. Retrying...")
        # Retry the task if it fails, up to max_retries times
        raise self.retry(exc=exc, countdown=60)  # Retry after 60 seconds


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email_task(self, user_id):
    """
    Send welcome email asynchronously after email verification with retry logic.
    Retries up to 3 times with 60 second delay between attempts.
    
    Args:
        user_id: ID of the verified user
    """
    try:
        user = CustomUser.objects.get(pk=user_id)
        
        subject = 'Welcome to Horizon Reality!'
        html_message = render_to_string('emails/welcome_email.html', {
            'user': user,
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Welcome email sent successfully to {user.email}")
        return f"Welcome email sent successfully to {user.email}"
    
    except CustomUser.DoesNotExist:
        logger.error(f"User with ID {user_id} not found")
        return f"User with ID {user_id} not found"
    
    except Exception as exc:
        logger.warning(f"Error sending welcome email to user {user_id}: {str(exc)}. Retrying...")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_newsletter_welcome_email_task(self, user_email, user_name, unsubscribe_token):
    """
    Send newsletter welcome email asynchronously with retry logic.
    Retries up to 3 times with 60 second delay between attempts.
    
    Args:
        user_email: Email address of the subscriber
        user_name: Name of the subscriber
        unsubscribe_token: Token for unsubscribing
    """
    try:
        subject = 'Welcome to Horizon Reality Newsletter!'
        html_message = render_to_string('emails/newsletter_welcome.html', {
            'user_name': user_name,
            'unsubscribe_token': unsubscribe_token,
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Newsletter welcome email sent successfully to {user_email}")
        return f"Newsletter welcome email sent successfully to {user_email}"
    
    except Exception as exc:
        logger.warning(f"Error sending newsletter welcome email to {user_email}: {str(exc)}. Retrying...")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_weekly_property_newsletter(self):
    """
    Send weekly newsletter to all subscribed users with properties listed in the last 7 days.
    Retries up to 3 times with 5 minute delay between attempts.
    """
    try:
        subscribers = Newsletter.objects.filter(status='subscribed')
        if not subscribers.exists():
            logger.info("No subscribers found for weekly newsletter")
            return "No subscribers found"
        
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_properties = BuyProperties.objects.filter(
            created_at__gte=seven_days_ago,
            is_property_active=True
        ).order_by('-created_at')
        
        if not recent_properties.exists():
            logger.info("No new properties found for weekly newsletter")
            return "No new properties found"
        
        subject = f"Weekly Property Update - {recent_properties.count()} New Properties This Week"
        successful_sends = 0
        failed_sends = 0
        failed_emails = []
        
        for subscriber in subscribers:
            try:
                context = {
                    'subscriber_name': subscriber.name or 'Dear Subscriber',
                    'subscriber_email': subscriber.email,
                    'properties': recent_properties,
                    'property_count': recent_properties.count(),
                    'week_start': seven_days_ago.strftime('%B %d, %Y'),
                    'week_end': timezone.now().strftime('%B %d, %Y'),
                    'unsubscribe_token': subscriber.unsubscribe_token,
                }
                
                html_message = render_to_string('emails/weekly_newsletter.html', context)
                plain_message = strip_tags(html_message)
                
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[subscriber.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                successful_sends += 1
                logger.info(f"Weekly newsletter sent to {subscriber.email}")
            
            except Exception as e:
                failed_sends += 1
                failed_emails.append(subscriber.email)
                logger.error(f"Failed to send newsletter to {subscriber.email}: {str(e)}")
                continue
        
        result_message = f"Newsletter sent to {successful_sends} subscribers. {failed_sends} failed."
        if failed_emails:
            result_message += f" Failed emails: {', '.join(failed_emails)}"
        
        logger.info(result_message)
        return result_message
    
    except Exception as exc:
        logger.error(f"Error in weekly newsletter task: {str(exc)}. Retrying...")
        raise self.retry(exc=exc, countdown=300)  # Retry after 5 minutes


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_new_property_notification(self, property_id):
    """
    Send immediate notification to subscribers when a new property is listed.
    Retries up to 3 times with 60 second delay between attempts.
    
    Args:
        property_id: ID of the newly listed property
    """
    try:
        property_obj = BuyProperties.objects.get(id=property_id, is_property_active=True)
        subscribers = Newsletter.objects.filter(status='subscribed')
        
        if not subscribers.exists():
            logger.info("No subscribers found for new property notification")
            return "No subscribers found"
        
        subject = f"New Property Alert: {property_obj.title or 'Property Available'}"
        successful_sends = 0
        failed_sends = 0
        failed_emails = []
        
        for subscriber in subscribers:
            try:
                context = {
                    'subscriber_name': subscriber.name or 'Dear Subscriber',
                    'property': property_obj,
                    'unsubscribe_token': subscriber.unsubscribe_token,
                }
                
                html_message = render_to_string('emails/new_property_alert.html', context)
                plain_message = strip_tags(html_message)
                
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[subscriber.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                successful_sends += 1
                logger.info(f"New property notification sent to {subscriber.email}")
            
            except Exception as e:
                failed_sends += 1
                failed_emails.append(subscriber.email)
                logger.error(f"Failed to send property notification to {subscriber.email}: {str(e)}")
                continue
        
        result_message = f"Notification sent to {successful_sends} subscribers. {failed_sends} failed."
        if failed_emails:
            result_message += f" Failed emails: {', '.join(failed_emails)}"
        
        logger.info(result_message)
        return result_message
    
    except BuyProperties.DoesNotExist:
        logger.error(f"Property with ID {property_id} not found")
        return f"Property with ID {property_id} not found"
    
    except Exception as exc:
        logger.error(f"Error sending new property notification: {str(exc)}. Retrying...")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=2, default_retry_delay=120)
def send_contact_form_notification(self, submission_id):
    """
    Send notification email when someone submits the contact form.
    Retries up to 2 times with 2 minute delay between attempts.
    
    Args:
        submission_id: ID of the contact form submission
    """
    try:
        from .models import ContactSubmission
        
        submission = ContactSubmission.objects.get(id=submission_id)
        
        subject = f"New Contact Form Submission from {submission.name}"
        html_message = render_to_string('emails/contact_form_notification.html', {
            'submission': submission,
        })
        plain_message = strip_tags(html_message)
        
        # Send to admin email
        admin_email = getattr(settings, 'ADMIN_EMAIL', settings.DEFAULT_FROM_EMAIL)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [admin_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Contact form notification sent for submission {submission_id}")
        return f"Contact form notification sent successfully"
    
    except ContactSubmission.DoesNotExist:
        logger.error(f"Contact submission with ID {submission_id} not found")
        return f"Contact submission with ID {submission_id} not found"
    
    except Exception as exc:
        logger.error(f"Error sending contact form notification: {str(exc)}. Retrying...")
        raise self.retry(exc=exc, countdown=120)
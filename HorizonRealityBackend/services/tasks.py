from celery import shared_task 
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Newsletter, BuyProperties, CustomUser

@shared_task
def send_weekly_property_newsletter():
    """
    Send weekly newsletter to all subscribed users with properties listed in the last 7 days
    """
    try:
        subscribers = Newsletter.objects.filter(status='subscribed')
        if not subscribers.exists():
            return "No subscribers found"
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_properties = BuyProperties.objects.filter(
            created_at__gte=seven_days_ago,
            is_property_active=True
        ).order_by('-created_at')
        if not recent_properties.exists():
            return "No new properties found"
        subject = f"Weekly Property Update - {recent_properties.count()} New Properties This Week"
        successful_sends = 0
        failed_sends = 0
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
                    # 'base_url': getattr(settings, 'BASE_URL', 'http://localhost:8000'),
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
            except Exception as e:
                failed_sends += 1
                continue
        result_message = f"Newsletter sent to {successful_sends} subscribers. {failed_sends} failed."
        return result_message
    except Exception as e:
        return f"Error: {str(e)}"

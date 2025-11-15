from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
import logging

def send_newsletter_welcome_email(user_email, user_name=None, unsubscribe_token=None):
    """
    Send welcome email to new newsletter subscriber
    """
    try:
        context = {
            'user_name': user_name or 'Valued Customer',
            'company_name': 'Horizon Reality',
            # 'website_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'https://your-domain.com',
            # 'unsubscribe_url': f"{settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'https://your-domain.com'}/newsletter/unsubscribe/{unsubscribe_token}/" if unsubscribe_token else None,
        }
        try:
            html_message = render_to_string('emails/newsletter_welcome.html', context)
        except Exception as e:
            html_message = f"""
            <html>
            <body>
                <h2>Welcome to {context['company_name']} Newsletter! 🏡</h2>
                <p>Hello {context['user_name']},</p>
                <p>Thank you for subscribing to our newsletter! You'll receive the latest updates about real estate opportunities.</p>
                <p>Best regards,<br>The {context['company_name']} Team</p>
            </body>
            </html>
            """
        try:
            plain_message = render_to_string('emails/newsletter_welcome.txt', context)
        except Exception as e:
            print(f"ERROR rendering plain text template: {str(e)}")
            plain_message = strip_tags(html_message)
        subject = 'Welcome to Horizon Reality Newsletter! 🏡'
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"ERROR in send_newsletter_welcome_email: {str(e)}")
        return False
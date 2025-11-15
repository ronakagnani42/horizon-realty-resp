from django.shortcuts import render, redirect, get_object_or_404
from .forms import ContactForm,UserRegistrationForm, LoginForm, UpdateProfileForm
from django.contrib import messages
from .models import ContactSubmission, CustomUser, ContactInformation, Newsletter
from django.contrib.auth import login, authenticate, logout
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.utils import timezone
from .utils import send_newsletter_welcome_email
from datetime import timedelta
from django.contrib.auth.decorators import login_required

def register(request):
    """
    Handles user registration with email verification and newsletter subscription.
    - Creates inactive user
    - Handles newsletter subscription
    - Sends verification email
    - Sends newsletter welcome email if subscribed
    - User is activated upon email verification
    """
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False 
            user.save()
            newsletter_subscribed = form.cleaned_data.get('newsletter_subscription', False)
            newsletter_created = False
            newsletter_obj = None
            if newsletter_subscribed:
                try:
                    newsletter_obj, newsletter_created = Newsletter.subscribe_email(
                        email=user.email,
                        name=f"{user.first_name} {user.last_name}".strip(),
                        source='registration'
                    )
                    user.newsletter_subscribed = True
                    user.save()
                except Exception as e:
                    print(f"ERROR creating newsletter subscription: {str(e)}")
            else:
                print("Newsletter subscription not selected")
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            current_site = get_current_site(request)
            verification_url = request.build_absolute_uri(
                reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
            )
            try:
                subject = 'Verify Your Horizon Reality Account'
                html_message = render_to_string('emails/verification_email.html', {
                    'user': user,
                    'verification_url': verification_url,
                    'domain': current_site.domain,
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
                print(f"Verification email sent successfully to {user.email}")
            except Exception as e:
                print(f"ERROR sending verification email: {str(e)}")
            if newsletter_subscribed and newsletter_obj:
                print("Newsletter subscription created. Welcome email will be sent after verification.")
            else:
                print(f"Newsletter welcome email will not be sent. Subscribed: {newsletter_subscribed}, Newsletter obj exists: {newsletter_obj is not None}")
            success_message = 'Registration successful! A confirmation email has been sent to your inbox.'
            if newsletter_subscribed:
                success_message += ' You will receive a newsletter welcome email after verifying your account.'
            return JsonResponse({
                'success': True,
                'message': success_message,
            })
        else:
            print(f"Form validation failed. Errors: {form.errors}")
            return JsonResponse({
                'success': False,
                'message': 'There were errors in your registration form.',
                'errors': form.errors
            }, status=400)
    else:
        form = UserRegistrationForm()
    return render(request, 'users/registeration.html', {'form': form})

def verify_email(request, uidb64, token):
    """
    Activates user account upon email verification
    and sends welcome email.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.is_verified = True
            user.save()
            try:
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
            except Exception as e:
                print(f"ERROR sending welcome email: {str(e)}")
            if user.newsletter_subscribed:
                try:
                    newsletter_obj = Newsletter.objects.get(email=user.email)
                    result = send_newsletter_welcome_email(
                        user_email=user.email,
                        user_name=f"{user.first_name} {user.last_name}".strip(),
                        unsubscribe_token=str(newsletter_obj.unsubscribe_token)
                    )
                except Newsletter.DoesNotExist:
                    print(f"Newsletter object not found for {user.email}")
                except Exception as e:
                    print(f"ERROR sending newsletter welcome email during verification: {str(e)}")
            else:
                print("User is not subscribed to newsletter, skipping newsletter welcome email")
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'users/verification_invalid.html')
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist) as e:
        return render(request, 'users/verification_invalid.html')

def login_view(request):
    '''
    Handles user login.
    - On GET: Displays the login form.
    - On POST: Authenticates user credentials and logs them in if valid.
    '''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error('password', 'Invalid email or password.')
        return render(request, 'users/login.html', {'form': form})
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})

def contact_us_view(request):
    '''
    Displays and processes the "Contact Us" form.
    - On GET: Shows the contact form with dynamic contact information.
    - On POST: Validates and saves the form submission and gives feedback.
    '''
    contact_info = ContactInformation.objects.filter(is_main_office=True).first()
    if not contact_info:
        contact_info = ContactInformation.objects.first()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Your message has been sent. Thank you!")
                return redirect('contact-us')
            except Exception as e:
                messages.error(request, "There was an error sending your message. Please try again.")
        else:
            if 'email' in form.errors:
                for error in form.errors['email']:
                    messages.error(request, error)
            else:
                messages.error(request, "Please check your form and try again.")
    else:
        form = ContactForm() 
    context = {
        'contact_info': contact_info,
        'form': form,
    }
    return render(request, 'users/contact_us.html', context)

def logout_view(request):
    '''
    Logs out the current user and redirects them to the homepage.
    '''
    logout(request)
    return redirect('home')

@login_required
def update_profile_view(request):
    """
    View for updating user profile information.
    GET: Display form with current user data pre-filled
    POST: Process form submission and update user profile
    """
    user = request.user
    can_update, days_remaining = can_user_update_profile(user)
    if request.method == 'POST':
        if not can_update:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'You cannot update your profile for another {days_remaining} days.',
                    'restriction_active': True,
                    'days_remaining': days_remaining
                })
            else:
                messages.error(request, f'You cannot update your profile for another {days_remaining} days.')
                return render(request, 'users/update_profile.html', {
                    'form': UpdateProfileForm(instance=user),
                    'user': user,
                    'can_update': can_update,
                    'days_remaining': days_remaining
                })
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return handle_ajax_profile_update(request, user)
        form = UpdateProfileForm(request.POST, instance=user)
        if form.is_valid():
            try:
                updated_user = form.save(commit=False)
                updated_user.email = user.email
                updated_user.date_joined = user.date_joined
                if updated_user.user_type == 'broker':
                    if not updated_user.firm_name:
                        messages.error(request, "Firm name is required for brokers.")
                        return render(request, 'users/update_profile.html', {
                            'form': form,
                            'user': user,
                            'can_update': can_update,
                            'days_remaining': days_remaining
                        })
                updated_user.last_profile_update = timezone.now()
                updated_user.save()
                messages.success(request, "Your profile has been updated successfully! You won't be able to update it again for 15 days.")
                return redirect('profile_view')
            except ValidationError as e:
                messages.error(request, f"Validation error: {e}")
            except Exception as e:
                messages.error(request, f"An error occurred while updating your profile: {e}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
    else:
        form = UpdateProfileForm(instance=user)
        form.fields['email'].initial = user.email
        form.fields['date_joined'].initial = user.date_joined
    context = {
        'form': form,
        'user': user,
        'page_title': 'Update Profile',
        'can_update': can_update,
        'days_remaining': days_remaining,
        'last_update': user.last_profile_update if hasattr(user, 'last_profile_update') else None
    }
    return render(request, 'users/update_profile.html', context)


def handle_ajax_profile_update(request, user):
    """
    Handle AJAX form submission for profile updates
    """
    try:
        can_update, days_remaining = can_user_update_profile(user)
        if not can_update:
            return JsonResponse({
                'success': False,
                'message': f'You cannot update your profile for another {days_remaining} days.',
                'restriction_active': True,
                'days_remaining': days_remaining
            })
        form = UpdateProfileForm(request.POST, instance=user)
        if form.is_valid():
            updated_user = form.save(commit=False)
            updated_user.email = user.email
            updated_user.date_joined = user.date_joined
            if updated_user.user_type == 'broker' and not updated_user.firm_name:
                return JsonResponse({
                    'success': False,
                    'message': 'Firm name is required for brokers.',
                    'errors': {'firm_name': ['This field is required for brokers.']}
                })
            updated_user.last_profile_update = timezone.now()
            updated_user.save()
            return JsonResponse({
                'success': True,
                'message': 'Your profile has been updated successfully! You won\'t be able to update it again for 15 days.',
                'user_data': {
                    'first_name': updated_user.first_name,
                    'last_name': updated_user.last_name,
                    'contact_number': updated_user.contact_number,
                    'user_type': updated_user.get_user_type_display(),
                    'firm_type': updated_user.get_firm_type_display() if updated_user.firm_type else '',
                    'firm_name': updated_user.firm_name or '',
                },
                'restriction_active': True,
                'next_update_allowed': (timezone.now() + timedelta(days=15)).isoformat()
            })
        
        else:
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = [str(error) for error in field_errors]
            return JsonResponse({
                'success': False,
                'message': 'Please correct the errors below.',
                'errors': errors
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An unexpected error occurred: {str(e)}'
        })

def can_user_update_profile(user):
    """
    Check if user can update their profile based on 15-day restriction
    Returns (can_update: bool, days_remaining: int)
    """
    if not hasattr(user, 'last_profile_update') or user.last_profile_update is None:
        return True, 0
    time_since_update = timezone.now() - user.last_profile_update
    restriction_period = timedelta(days=15)
    if time_since_update >= restriction_period:
        return True, 0
    else:
        days_remaining = (restriction_period - time_since_update).days + 1
        return False, days_remaining

@login_required
def profile_view(request):
    """
    View for displaying user profile (read-only)
    """
    can_update, days_remaining = can_user_update_profile(request.user)
    context = {
        'user': request.user,
        'page_title': 'My Profile',
        'can_update': can_update,
        'days_remaining': days_remaining,
        'last_update': request.user.last_profile_update if hasattr(request.user, 'last_profile_update') else None
    }
    return render(request, 'users/profile_view.html', context)

@login_required
def get_user_data_json(request):
    """
    Return current user data as JSON
    Useful for JavaScript functionality
    """
    user = request.user
    can_update, days_remaining = can_user_update_profile(user)
    data = {
        'email': user.email,
        'first_name': user.first_name or '',
        'last_name': user.last_name or '',
        'contact_number': user.contact_number or '',
        'user_type': user.user_type,
        'user_type_display': user.get_user_type_display(),
        'firm_type': user.firm_type or '',
        'firm_type_display': user.get_firm_type_display() if user.firm_type else '',
        'firm_name': user.firm_name or '',
        'date_joined': user.date_joined.isoformat() if user.date_joined else '',
        'is_broker': user.user_type == 'broker',
        'can_update_profile': can_update,
        'days_remaining_for_update': days_remaining,
        'last_profile_update': user.last_profile_update.isoformat() if hasattr(user, 'last_profile_update') and user.last_profile_update else None,
    }
    return JsonResponse(data)
# users/signals.pyfrom django.dispatch import receiver
from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(user_signed_up)
def populate_user_from_google(request, user, sociallogin=None, **kwargs):
    """
    Automatically populate user information from Google account when user signs up via Google OAuth.
    This signal is triggered after a new user account is created through social login.
    """
    if sociallogin and sociallogin.account.provider == 'google':
        extra_data = sociallogin.account.extra_data
        if not user.first_name and 'given_name' in extra_data:
            user.first_name = extra_data.get('given_name', '')
        
        if not user.last_name and 'family_name' in extra_data:
            user.last_name = extra_data.get('family_name', '')
        
        user.is_verified = True
        user.is_active = True
        user.profile_complete = False
        user.save()
        print(f"✅ Google signup successful: {user.email}")
        print(f"   Name: {user.first_name} {user.last_name}")
        print(f"   Profile complete: {user.profile_complete}")
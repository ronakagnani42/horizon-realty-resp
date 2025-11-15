from django import forms
from .models import ContactSubmission, CustomUser
from django.core.validators import RegexValidator, EmailValidator, ValidationError


class ContactForm(forms.ModelForm):
    email = forms.EmailField(
        validators=[EmailValidator(message="Please enter a valid email address.")],
        error_messages={'required': 'Email is required.', 'invalid': 'Please enter a valid email address.'}
    )
    class Meta:
        model = ContactSubmission
        fields = ['name', 'email', 'subject', 'message']

class UserRegistrationForm(forms.ModelForm):
    first_name_validator = RegexValidator(
        regex=r'^[a-zA-Z\s]*$',
        message='First Name can only contain letters and spaces.'
    )

    last_name_validator = RegexValidator(
        regex=r'^[a-zA-Z\s]*$',
        message='Last Name can only contain letters and spaces.'
    )
    
    phone_validator = RegexValidator(
    regex=r'^\d{10}$',
    message='Phone number must be exactly 10 digits.'
    )
    user_type = forms.ChoiceField(
        choices=CustomUser.USER_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'user_type'
        })
    )
    firm_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your firm name',
            'class': 'form-control',
            'id': 'firm_name'
        })
    )
    first_name = forms.CharField(
        min_length=2,
        max_length=30,
        validators=[first_name_validator],
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your first name',
            'class': 'form-control'
        })
    )

    last_name = forms.CharField(
        min_length=2,
        max_length=30,
        validators=[last_name_validator],
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your last name',
            'class': 'form-control'
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email',
            'class': 'form-control'
        })
    )

    contact_number = forms.CharField(
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your contact number',
            'class': 'form-control'
        })
    )

    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'class': 'form-control'
        })
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm your password',
            'class': 'form-control'
        })
    )
    newsletter_subscription = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'newsletter'
        }),
        label="Subscribe to our newsletter for latest property updates"
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'contact_number','user_type','firm_name', 'password', 'confirm_password','newsletter_subscription']

    def clean_first_name(self):
        """Validate first name"""
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            first_name = first_name.title()
            first_name = ' '.join(first_name.split())
        return first_name

    def clean_last_name(self):
        """Validate last name"""
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            last_name = last_name.title()
            last_name = ' '.join(last_name.split())
        return last_name

    def clean_email(self):
        """Validate email"""
        email = self.cleaned_data.get('email').lower()
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already registered.")
        return email

    def clean_contact_number(self):
        """Validate contact number"""
        contact_number = self.cleaned_data.get('contact_number')
        contact_number = ''.join(filter(lambda x: x.isdigit() or x == '+', contact_number))
        if CustomUser.objects.filter(contact_number=contact_number).exists():
            raise forms.ValidationError("Contact number is already registered.")
        return contact_number

    def clean_password(self):
        """Validate password complexity"""
        password = self.cleaned_data.get('password')
        if password:
            if len(password) < 8:
                raise forms.ValidationError("Password must be at least 8 characters long.")
            
            if not any(char.isupper() for char in password):
                raise forms.ValidationError("Password must contain at least one uppercase letter.")
            
            if not any(char.islower() for char in password):
                raise forms.ValidationError("Password must contain at least one lowercase letter.")
            
            if not any(char.isdigit() for char in password):
                raise forms.ValidationError("Password must contain at least one number.")
            
            special_characters = "[!@#$%^&*(),.?\":{}|<>]"
            if not any(char in special_characters for char in password):
                raise forms.ValidationError("Password must contain at least one special character.")

        return password

    def clean(self):
        """Final validation"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError({
                    'confirm_password': "Passwords do not match."
                })

        return cleaned_data

    def save(self, commit=True):
        """Save the user instance and handle newsletter subscription"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.newsletter_subscribed = self.cleaned_data.get('newsletter_subscription', False)
        
        if commit:
            user.save()
            
            # Handle newsletter subscription
            if self.cleaned_data.get('newsletter_subscription'):
                from .models import Newsletter  # Import here to avoid circular imports
                Newsletter.subscribe_email(
                    email=user.email,
                    name=f"{user.first_name} {user.last_name}".strip(),
                    source='registration'
                )
        
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        }),
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Please enter a valid email address.'
        }
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        }),
        error_messages={
            'required': 'Password is required.'
        }
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            try:
                user = CustomUser.objects.get(email=email)
                if not user.check_password(password):
                    self.add_error('password', 'Incorrect password.')
            except CustomUser.DoesNotExist:
                self.add_error('email', 'Email does not exist.')

        return cleaned_data

class UpdateProfileForm(forms.ModelForm):
    """
    Form for updating user profile information.
    Some fields are read-only, others are editable.
    """
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'readonly': True,
            'style': 'background-color: #f8f9fa; cursor: not-allowed;'
        }),
        label='Email Address',
        required=False
    )
    
    date_joined = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'readonly': True,
            'style': 'background-color: #f8f9fa; cursor: not-allowed;'
        }),
        label='Member Since',
        required=False
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'email',        
            'first_name',      
            'last_name',       
            'contact_number', 
            'user_type',      
            'firm_type',  
            'firm_name',
        ]
        
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'readonly': True,
                'style': 'background-color: #f8f9fa; cursor: not-allowed;'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your last name'
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your contact number'
            }),
            'user_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'firm_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'firm_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter firm name (required for brokers)'
            }),
            
        }
        
        labels = {
            'email': 'Email Address',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'contact_number': 'Contact Number',
            'user_type': 'User Type',
            'firm_type': 'Firm Type',
            'firm_name': 'Firm Name',
           
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            self.fields['email'].initial = self.instance.email
        
        self.fields['email'].required = False
    
    def save(self, commit=True):
        """
        Override save to exclude read-only fields from being saved
        """
        if 'email' in self.changed_data:
            self.changed_data.remove('email')
       
        
        return super().save(commit=commit)
        """
        Validate that firm_name is provided when user_type is 'broker'
        """
        firm_name = self.cleaned_data.get('firm_name')
        user_type = self.cleaned_data.get('user_type')
        
        if user_type == 'broker' and not firm_name:
            raise ValidationError("Firm name is required for brokers.")
        
        return firm_name
    
    def clean_contact_number(self):
        """
        Basic validation for contact number format
        """
        contact_number = self.cleaned_data.get('contact_number')
        
        if contact_number:
            cleaned_number = ''.join(filter(str.isdigit, contact_number))
            
            if len(cleaned_number) < 10:
                raise ValidationError("Contact number must be at least 10 digits long.")
            
            if len(cleaned_number) > 15:
                raise ValidationError("Contact number cannot exceed 15 digits.")
        
        return contact_number
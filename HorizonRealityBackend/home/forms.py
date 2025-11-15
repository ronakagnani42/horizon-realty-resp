import re
from services.models import SellResidentialProperties, PropertyLocation, SellCommercialProperties,BuyProperties
from django import forms
from django.forms import ModelMultipleChoiceField, MultipleChoiceField
from users.models import CustomUser
from django.core.validators import RegexValidator
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import ValidationError

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
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'contact_number','user_type','firm_name', 'password', 'confirm_password']

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
        """Save the user instance"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
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

class CustomPasswordResetForm(SetPasswordForm):
    """
    Custom form for password reset that implements specific password rules:
    - At least 8 characters
    - Contains at least one number
    - Contains at least one uppercase letter
    - Contains at least one special character
    """
    
    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError("The two password fields didn't match.")
        
        if len(password2) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        
        if not re.search(r'\d', password2):
            raise ValidationError("Password must contain at least one number.")
        
        if not re.search(r'[A-Z]', password2):
            raise ValidationError("Password must contain at least one uppercase letter.")
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>/?]', password2):
            raise ValidationError("Password must contain at least one special character.")
        
        return password2

class SellResidentialPropertyForm(forms.ModelForm):
    locations = forms.ModelChoiceField(
        queryset=PropertyLocation.objects.all(),
        empty_label="Select Location",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_for_sale = forms.BooleanField(required=False, initial=True, label="Sell")
    is_for_rent = forms.BooleanField(required=False, label="Rent Out")
    is_for_lease = forms.BooleanField(required=False, label="Lease Out")
    is_for_new = forms.BooleanField(required=False, label="New")
    video = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        help_text="Upload a property video (max 50MB; formats: mp4, avi, mov, wmv, mkv, flv, webm)"
    )
    
    class Meta:
        model = SellResidentialProperties
        fields = [
            'project_name', 'configuration',
             'area', 'budget','floor_num','unit_num','property_subtype', 'locations','additional_details','image','video','contact_name',
            'contact_email','contact_number',
        ]
        widgets = {
            'project_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project Name'}),
            'configuration': forms.RadioSelect(),
            'area': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter property area in square feet'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your expected price or rent'}),
            'floor_num': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Floor Number (e.g., 5)'}),
            'unit_num': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unit Number (e.g., A-101, B-205)'}),
            'property_subtype': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Property Subtype'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'video': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'additional_details': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Additional details about the property'}),
            'contact_name': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Your Name'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control','placeholder': 'Your Email'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Your Contact Number'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project_name'].required = False
        self.fields['configuration'].required = False
        self.fields['contact_email'].required = True
        self.fields['contact_number'].required = True
        self.fields['contact_name'].required = True

class SellCommercialPropertyForm(forms.ModelForm):
    locations = forms.ModelChoiceField(
        queryset=PropertyLocation.objects.all(),
        empty_label="Select Location",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
      
    is_for_resale = forms.BooleanField(required=False, initial=True, label="Resale")
    is_for_rent = forms.BooleanField(required=False, label="Rent Out")
    is_for_lease = forms.BooleanField(required=False, label="Lease Out")
    is_for_new = forms.BooleanField(required=False, label="New")
    video = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        help_text="Upload a property video (max 50MB; formats: mp4, avi, mov, wmv, mkv, flv, webm)"
    )
    
    class Meta:
        model = SellCommercialProperties
        fields = [
            'project_name','commercial_type','furnishing','area',  'floor_num', 'unit_num','budget','property_subtype', 'additional_details','locations', 'image', 'video','contact_name',
            'contact_email','contact_number',
        ]
        widgets = {
            'project_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project Name'}),
            'commercial_type': forms.RadioSelect(),
            'furnishing': forms.RadioSelect(),
            'area': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter property area in square feet'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your expected price or rent'}),
            'property_subtype': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Property Subtype'}),
            'floor_num': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Floor Number (e.g., 5)'}),
            'unit_num': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unit Number (e.g., A-101, B-205)'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'video': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'additional_details': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Additional details about the property'}),
            'contact_name': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Your Name'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control','placeholder': 'Your Email'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Your Contact Number'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)        
        self.fields['project_name'].required = False
        self.fields['contact_email'].required = True
        self.fields['contact_number'].required = True
        self.fields['contact_name'].required = True

class BuyPropertySearchForm(forms.Form):
    status = forms.MultipleChoiceField(
        choices=BuyProperties.STATUS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        initial=['new']  
    )
    
    configuration = forms.MultipleChoiceField(
        choices=BuyProperties.RESIDENTIAL_CONFIG_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        initial=['2bhk', '3bhk']
    )
    
    area_range = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'type': 'range',
            'min': '300',          
            'max': '10000',         
            'step': '100',          
            'value': '1500',      
            'class': 'form-range',
            'id': 'area-res-slider'
        }),
        initial=1500,
        required=False
    )
    
    budget_range = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'type': 'range',
            'min': '10000',       
            'max': '100000000', 
            'step': '50000',   
            'value': '5000000', 
            'class': 'form-range',
            'id': 'budget-res-slider'
        }),
        initial=5000000,
        required=False
    )
    
    locations = forms.ModelMultipleChoiceField(
        queryset=PropertyLocation.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        to_field_name='id'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            default_locations = PropertyLocation.objects.filter(
                name__in=['SG Highway', 'Satellite']
            ).values_list('id', flat=True)
            self.fields['locations'].initial = list(default_locations)
    
    def clean_status(self):
        """Ensure status is always a list"""
        status = self.cleaned_data.get('status')
        if isinstance(status, str):
            return [status]
        return status or []
    
    def clean_configuration(self):
        """Ensure configuration is always a list"""
        configuration = self.cleaned_data.get('configuration')
        if isinstance(configuration, str):
            return [configuration]
        return configuration or []
    
    def clean_locations(self):
        """Ensure locations is always a list"""
        locations = self.cleaned_data.get('locations')
        if not locations:
            return []
        return locations


class BuyCommercialPropertySearchForm(forms.Form):
    status = forms.MultipleChoiceField(
        choices=BuyProperties.STATUS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        initial=['new']
    )
    
    configuration = forms.MultipleChoiceField(
        choices=BuyProperties.COMMERCIAL_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        initial=['showroom']
    )

    furnishing = forms.MultipleChoiceField(
        choices=BuyProperties.FURNISHING_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        initial=['furnished']
    )
    
    area_range = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'type': 'range',
            'min': '300',          
            'max': '10000',         
            'step': '100',         
            'value': '1500',        
            'class': 'form-range',
            'id': 'area-res-slider' 
        }),
        initial=1500,
        required=False
    )
    
    budget_range = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'type': 'range',
            'min': '10000',       
            'max': '100000000',    
            'step': '50000',      
            'value': '5000000',  
            'class': 'form-range',
            'id': 'budget-res-slider'
        }),
        initial=5000000,
        required=False
    )
    
    locations = forms.ModelMultipleChoiceField(
        queryset=PropertyLocation.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        to_field_name='id'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            default_locations = PropertyLocation.objects.filter(
                name__in=['SG Highway', 'Satellite']
            ).values_list('id', flat=True)
            self.fields['locations'].initial = list(default_locations)
    
    def clean_status(self):
        """Ensure status is always a list"""
        status = self.cleaned_data.get('status')
        if isinstance(status, str):
            return [status]
        return status or []

    def clean_furnishing(self):
        """Ensure furnishing is always a list"""
        furnishing = self.cleaned_data.get('furnishing')
        if isinstance(furnishing, str):
            return [furnishing]
        return furnishing or []

    
    def clean_configuration(self):
        """Ensure configuration is always a list"""
        configuration = self.cleaned_data.get('configuration')
        if isinstance(configuration, str):
            return [configuration]
        return configuration or []
    
    def clean_locations(self):
        """Ensure locations is always a list"""
        locations = self.cleaned_data.get('locations')
        if not locations:
            return []
        return locations
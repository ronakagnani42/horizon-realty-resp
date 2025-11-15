# forms.py
from django import forms
from .models import *
from django.core.validators import RegexValidator
import re
class PropertyCalculatorForm(forms.ModelForm):
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter email address'}
        )
    )
    
    class Meta:
        model = PropertyCalculatorInquiry
        fields = [
            'title', 'property_type', 'floor', 'location', 'flat_society_name', 
            'area', 'property_life', 'owner_name', 'phone_number',
            'photo', 'video', 'document', 'additional_info', 'email'  # Added video field
        ]
        widgets = {
            'title': forms.Select(
                attrs={'class': 'form-control', 'id': 'title'}
            ),
            'property_type': forms.Select(
                attrs={'class': 'form-control', 'id': 'property_type'}
            ),
            'floor': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter floor number'}
            ),
            'location': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter location'}
            ),
            'flat_society_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter flat/society name'}
            ),
            'area': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter area in sq ft'}
            ),
            'property_life': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter property age in years'}
            ),
            'owner_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter owner name'}
            ),
            'phone_number': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}
            ),
            'photo': forms.FileInput(
                attrs={'class': 'file-input', 'accept': 'image/*'}
            ),
            'video': forms.FileInput(
                attrs={'class': 'file-input', 'accept': 'video/*'}
            ),
            'document': forms.FileInput(
                attrs={'class': 'file-input', 'accept': '.pdf,.doc,.docx'}
            ),
            'additional_info': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter any additional information about your property'}
            ),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['property_type'].choices = [('', 'Select Property Type')]
        
        if kwargs.get('instance'):
            instance = kwargs.get('instance')
            if instance.title == 'residential':
                self.fields['property_type'].choices += PropertyCalculatorInquiry.RESIDENTIAL_TYPE_CHOICES
            elif instance.title == 'commercial':
                self.fields['property_type'].choices += PropertyCalculatorInquiry.COMMERCIAL_TYPE_CHOICES
    
    def clean_phone_number(self):
        """Validate phone number format."""
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            phone_number = re.sub(r'[\s\-\(\)]', '', phone_number)
            
            if not phone_number.isdigit():
                raise forms.ValidationError("Phone number must contain only digits.")
            if len(phone_number) < 10 or len(phone_number) > 15:
                raise forms.ValidationError("Phone number must be between 10 and 15 digits.")
                
        return phone_number
    
    def clean_email(self):
        """Validate email format (if you've added the email field)."""
        email = self.cleaned_data.get('email')
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise forms.ValidationError("Please enter a valid email address.")
        return email
    
    def clean_video(self):
        """Validate video file format and size."""
        video = self.cleaned_data.get('video')
        if video:
            if video.size > 50 * 1024 * 1024:
                raise forms.ValidationError("Video file size must be less than 50MB.")
            
            import os
            valid_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv']
            file_extension = os.path.splitext(video.name)[1].lower()
            if file_extension not in valid_extensions:
                raise forms.ValidationError("Please upload a valid video file (MP4, AVI, MOV, WMV, FLV, WebM, MKV).")
        
        return video
    
class InteriorDesignRequestForm(forms.ModelForm):
    """Form for Interior Design Request"""
    
    class Meta:
        model = InteriorDesignRequest
        fields = ['name', 'phone_number', 'property_types', 'sqft', 'service_types']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Phone Number',
                'type': 'tel'
            }),
            'property_types': forms.Select(attrs={
                'class': 'form-control'
            }),
            'sqft': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter property area in square feet'
            }),
            'service_types': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        
        labels = {
            'name': 'Your Name',
            'phone_number': 'Phone Number',
            'property_types': 'Property Type',
            'sqft': 'Sqft (SBA)',
            'service_types': 'Service Type',
        }
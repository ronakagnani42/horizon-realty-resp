  document.addEventListener('DOMContentLoaded', function() {
  // Form step navigation
  const step1 = document.getElementById('formStep1');
  const step2 = document.getElementById('formStep2');
  const step3 = document.getElementById('formStep3');
  
  const stepIndicator1 = document.getElementById('step1');
  const stepIndicator2 = document.getElementById('step2');
  const stepIndicator3 = document.getElementById('step3');
  
  // Required field IDs for each step
  const step1RequiredFields = ['title', 'property_type', 'id_location', 'id_flat_society_name', 'id_area', 'id_property_life'];
  const step2RequiredFields = ['id_owner_name', 'id_phone_number'];
  const step3RequiredFields = ['{{ form.photo.id_for_label }}'];
  
  // Validation functions
  function showFieldError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const formGroup = field.closest('.form-group');
    
    // Remove existing error styling and messages
    field.classList.remove('is-valid', 'is-invalid');
    const existingError = formGroup.querySelector('.validation-error');
    if (existingError) {
      existingError.remove();
    }
    
    // Add error styling and message
    field.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'validation-error text-danger mt-1';
    errorDiv.innerHTML = `<small><i class="bi bi-exclamation-circle me-1"></i>${message}</small>`;
    field.parentNode.appendChild(errorDiv);
  }
  
  function showFieldSuccess(fieldId) {
    const field = document.getElementById(fieldId);
    const formGroup = field.closest('.form-group');
    
    // Remove existing error styling and messages
    field.classList.remove('is-invalid');
    const existingError = formGroup.querySelector('.validation-error');
    if (existingError) {
      existingError.remove();
    }
    
    // Add success styling
    field.classList.add('is-valid');
  }
  
  function validateField(fieldId) {
    const field = document.getElementById(fieldId);
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';
    
    // Check if field is empty
    if (!value) {
      isValid = false;
      errorMessage = 'This field is required';
    } else {
      // Field-specific validations
      switch (fieldId) {
        case 'title':
          if (!['residential', 'commercial'].includes(value)) {
            isValid = false;
            errorMessage = 'Please select a valid property category';
          }
          break;
          
        case 'property_type':
          if (!value) {
            isValid = false;
            errorMessage = 'Please select a property type';
          }
          break;
          
        case 'location':
          if (value.length < 3) {
            isValid = false;
            errorMessage = 'Location must be at least 3 characters long';
          }
          break;
          
        case 'flat_society_name':
          if (value.length < 2) {
            isValid = false;
            errorMessage = 'Name must be at least 2 characters long';
          }
          break;
          
        case 'area':
          const areaValue = parseFloat(value);
          if (isNaN(areaValue) || areaValue <= 0) {
            isValid = false;
            errorMessage = 'Please enter a valid area in square feet';
          } else if (areaValue < 100) {
            isValid = false;
            errorMessage = 'Area must be at least 100 sq ft';
          }
          break;
          
        case 'property_life':
          const ageValue = parseInt(value);
          if (isNaN(ageValue) || ageValue < 0) {
            isValid = false;
            errorMessage = 'Please enter a valid property age';
          } else if (ageValue > 100) {
            isValid = false;
            errorMessage = 'Property age cannot exceed 100 years';
          }
          break;
          
        case 'owner_name':
          if (value.length < 2) {
            isValid = false;
            errorMessage = 'Name must be at least 2 characters long';
          } else if (!/^[a-zA-Z\s]+$/.test(value)) {
            isValid = false;
            errorMessage = 'Name should only contain letters and spaces';
          }
          break;
          
        case 'phone_number':
          const phoneRegex = /^[6-9]\d{9}$/;
          if (!phoneRegex.test(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid 10-digit mobile number';
          }
          break;
          
        case '{{ form.photo.id_for_label }}':
          if (!field.files || field.files.length === 0) {
            isValid = false;
            errorMessage = 'Property photo is required';
          } else {
            const file = field.files[0];
            const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
            const maxSize = 5 * 1024 * 1024; // 5MB
            
            if (!allowedTypes.includes(file.type)) {
              isValid = false;
              errorMessage = 'Please upload a valid image file (JPG, PNG, GIF)';
            } else if (file.size > maxSize) {
              isValid = false;
              errorMessage = 'Image size should not exceed 5MB';
            }
          }
          break;
      }
    }
    
    if (isValid) {
      showFieldSuccess(fieldId);
    } else {
      showFieldError(fieldId, errorMessage);
    }
    
    return isValid;
  }
  
  function validateStep(requiredFields) {
    let allValid = true;
    
    requiredFields.forEach(fieldId => {
      if (!validateField(fieldId)) {
        allValid = false;
      }
    });
    
    return allValid;
  }
  
  function showStepError(message) {
    // Remove existing step error
    const existingError = document.querySelector('.step-validation-error');
    if (existingError) {
      existingError.remove();
    }
    
    // Create and show new error
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger step-validation-error mt-3';
    errorDiv.innerHTML = `<i class="bi bi-exclamation-triangle me-2"></i>${message}`;
    
    // Insert before the navigation buttons
    const currentStep = document.querySelector('.form-step[style*="block"], .form-step:not([style*="none"])');
    const buttonContainer = currentStep.querySelector('.text-center, .d-flex');
    buttonContainer.parentNode.insertBefore(errorDiv, buttonContainer);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
      if (errorDiv.parentNode) {
        errorDiv.remove();
      }
    }, 5000);
  }
  
  // Add real-time validation to all required fields
  [...step1RequiredFields, ...step2RequiredFields, ...step3RequiredFields].forEach(fieldId => {
    const field = document.getElementById(fieldId);
    if (field) {
      // Add event listeners for real-time validation
      field.addEventListener('blur', function() {
        validateField(fieldId);
      });
      
      field.addEventListener('input', function() {
        // Remove error styling while typing
        if (field.classList.contains('is-invalid')) {
          field.classList.remove('is-invalid');
          const errorDiv = field.closest('.form-group').querySelector('.validation-error');
          if (errorDiv) {
            errorDiv.remove();
          }
        }
      });
      
      // Special handling for file inputs
      if (field.type === 'file') {
        field.addEventListener('change', function() {
          validateField(fieldId);
        });
      }
    }
  });
  
  // Next buttons with validation
  document.getElementById('nextToStep2').addEventListener('click', function() {
    if (validateStep(step1RequiredFields)) {
      step1.style.display = 'none';
      step2.style.display = 'block';
      stepIndicator1.classList.add('completed');
      stepIndicator2.classList.add('active');
      
      // Remove any existing step errors
      const existingError = document.querySelector('.step-validation-error');
      if (existingError) {
        existingError.remove();
      }
    } else {
      showStepError('Please fill in all required fields correctly before proceeding.');
      
      // Scroll to first invalid field
      const firstInvalidField = document.querySelector('.is-invalid');
      if (firstInvalidField) {
        firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstInvalidField.focus();
      }
    }
  });
  
  document.getElementById('nextToStep3').addEventListener('click', function() {
    if (validateStep(step2RequiredFields)) {
      step2.style.display = 'none';
      step3.style.display = 'block';
      stepIndicator2.classList.add('completed');
      stepIndicator3.classList.add('active');
      
      // Remove any existing step errors
      const existingError = document.querySelector('.step-validation-error');
      if (existingError) {
        existingError.remove();
      }
    } else {
      showStepError('Please fill in all required fields correctly before proceeding.');
      
      // Scroll to first invalid field
      const firstInvalidField = document.querySelector('.is-invalid');
      if (firstInvalidField) {
        firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstInvalidField.focus();
      }
    }
  });
  
  // Back buttons (no validation needed)
  document.getElementById('backToStep1').addEventListener('click', function() {
    step2.style.display = 'none';
    step1.style.display = 'block';
    stepIndicator2.classList.remove('active');
    stepIndicator1.classList.remove('completed');
    
    // Remove any existing step errors
    const existingError = document.querySelector('.step-validation-error');
    if (existingError) {
      existingError.remove();
    }
  });
  
  document.getElementById('backToStep2').addEventListener('click', function() {
    step3.style.display = 'none';
    step2.style.display = 'block';
    stepIndicator3.classList.remove('active');
    stepIndicator2.classList.remove('completed');
    
    // Remove any existing step errors
    const existingError = document.querySelector('.step-validation-error');
    if (existingError) {
      existingError.remove();
    }
  });
  
  // File previews (existing code with validation integration)
  const photoInput = document.getElementById('{{ form.photo.id_for_label }}');
  const photoPreviewContainer = document.getElementById('photoPreviewContainer');
  const photoPreview = document.getElementById('photoPreview');
  const photoFileName = document.getElementById('photoFileName').querySelector('span');
  const removePhoto = document.getElementById('removePhoto');
  
  photoInput.addEventListener('change', function(e) {
    if (this.files && this.files[0]) {
      const file = this.files[0];
      
      // Validate file before showing preview
      if (validateField('{{ form.photo.id_for_label }}')) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
          photoPreview.src = e.target.result;
          photoFileName.textContent = file.name;
          photoPreviewContainer.style.display = 'block';
        };
        
        reader.readAsDataURL(file);
      } else {
        // Clear the input if validation fails
        this.value = '';
        photoPreviewContainer.style.display = 'none';
      }
    }
  });
  
  removePhoto.addEventListener('click', function() {
    photoInput.value = '';
    photoPreviewContainer.style.display = 'none';
    validateField('{{ form.photo.id_for_label }}'); // Re-validate to show error
  });
  
  const videoInput = document.getElementById('{{ form.video.id_for_label }}');
  const videoPreviewContainer = document.getElementById('videoPreviewContainer');
  const videoPreview = document.getElementById('videoPreview');
  const videoFileName = document.getElementById('videoFileName').querySelector('span');
  const removeVideo = document.getElementById('removeVideo');
  
  videoInput.addEventListener('change', function(e) {
    if (this.files && this.files[0]) {
      const file = this.files[0];
      const allowedTypes = ['video/mp4', 'video/mov', 'video/avi', 'video/wmv'];
      const maxSize = 50 * 1024 * 1024; // 50MB
      
      if (!allowedTypes.includes(file.type)) {
        showFieldError('{{ form.video.id_for_label }}', 'Please upload a valid video file (MP4, MOV, AVI, WMV)');
        this.value = '';
        return;
      }
      
      if (file.size > maxSize) {
        showFieldError('{{ form.video.id_for_label }}', 'Video size should not exceed 50MB');
        this.value = '';
        return;
      }
      
      const reader = new FileReader();
      
      reader.onload = function(e) {
        videoPreview.src = e.target.result;
        videoFileName.textContent = file.name;
        videoPreviewContainer.style.display = 'block';
      };
      
      reader.readAsDataURL(file);
      showFieldSuccess('{{ form.video.id_for_label }}');
    }
  });
  
  removeVideo.addEventListener('click', function() {
    videoInput.value = '';
    videoPreviewContainer.style.display = 'none';
  });
  
  // Document preview
  const documentInput = document.getElementById('{{ form.document.id_for_label }}');
  const documentPreviewContainer = document.getElementById('documentPreviewContainer');
  const documentFileName = document.getElementById('documentFileName').querySelector('span');
  const removeDocument = document.getElementById('removeDocument');
  
  documentInput.addEventListener('change', function(e) {
    if (this.files && this.files[0]) {
      const file = this.files[0];
      const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      const maxSize = 10 * 1024 * 1024; // 10MB
      
      if (!allowedTypes.includes(file.type)) {
        showFieldError('{{ form.document.id_for_label }}', 'Please upload a valid document file (PDF, DOC, DOCX)');
        this.value = '';
        return;
      }
      
      if (file.size > maxSize) {
        showFieldError('{{ form.document.id_for_label }}', 'Document size should not exceed 10MB');
        this.value = '';
        return;
      }
      
      documentFileName.textContent = file.name;
      documentPreviewContainer.style.display = 'block';
      showFieldSuccess('{{ form.document.id_for_label }}');
    }
  });
  
  removeDocument.addEventListener('click', function() {
    documentInput.value = '';
    documentPreviewContainer.style.display = 'none';
  });
  
  // Close alert messages
  document.querySelectorAll('.alert-close').forEach(function(button) {
    button.addEventListener('click', function() {
      this.parentElement.style.display = 'none';
    });
  });
  
  // Property type dynamic options
  const titleSelect = document.getElementById('title');
  const propertyTypeSelect = document.getElementById('property_type');
  
  const residentialOptions = [
    {value: '', text: 'Select Property Type'},
    {value: '1bhk', text: '1 BHK'},
    {value: '2bhk', text: '2 BHK'},
    {value: '3bhk', text: '3 BHK'},
    {value: '4bhk', text: '4 BHK'},
    {value: '5bhk', text: '5 BHK'},
    {value: 'duplex', text: 'Duplex'},
    {value: 'tenament', text: 'Tenament'},
    {value: 'bungalow', text: 'Bungalow'},
    {value: 'villa', text: 'Villa'},
    {value: 'other', text: 'Other'}
  ];
  
  const commercialOptions = [
    {value: '', text: 'Select Property Type'},
    {value: 'office', text: 'Office'},
    {value: 'showroom', text: 'Showroom'},
    {value: 'corporate floor', text: 'Corporate Floor'},
    {value: 'shop', text: 'Shop'},
    {value: 'other', text: 'Other'}
  ];
  
  function updatePropertyTypeOptions(options) {
    propertyTypeSelect.innerHTML = '';
    
    options.forEach(function(option) {
      const optionElement = document.createElement('option');
      optionElement.value = option.value;
      optionElement.textContent = option.text;
      propertyTypeSelect.appendChild(optionElement);
    });
    
    // Re-validate property type after options change
    if (step1RequiredFields.includes('property_type')) {
      validateField('property_type');
    }
  }
  
  // Set initial options based on current title value
  if (titleSelect.value === 'residential') {
    updatePropertyTypeOptions(residentialOptions);
  } else if (titleSelect.value === 'commercial') {
    updatePropertyTypeOptions(commercialOptions);
  }
  
  titleSelect.addEventListener('change', function() {
    if (this.value === 'residential') {
      updatePropertyTypeOptions(residentialOptions);
    } else if (this.value === 'commercial') {
      updatePropertyTypeOptions(commercialOptions);
    }
    
    // Validate title field after change
    validateField('title');
  });
  
  // Final form submission validation
  const form = document.getElementById('propertyInquiryForm');
  form.addEventListener('submit', function(e) {
    // Validate all required fields before submission
    const allRequiredFields = [...step1RequiredFields, ...step2RequiredFields, ...step3RequiredFields];
    let allValid = true;
    
    allRequiredFields.forEach(fieldId => {
      if (!validateField(fieldId)) {
        allValid = false;
      }
    });
    
    if (!allValid) {
      e.preventDefault();
      showStepError('Please fix all validation errors before submitting the form.');
      
      // Scroll to first invalid field
      const firstInvalidField = document.querySelector('.is-invalid');
      if (firstInvalidField) {
        firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstInvalidField.focus();
      }
    }
  });
});
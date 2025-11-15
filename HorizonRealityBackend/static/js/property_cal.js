document.addEventListener('DOMContentLoaded', function() {
    // Photo preview
    const photoInput = document.getElementById('{{ form.photo.id_for_label }}');
    const photoPreview = document.getElementById('photoPreview');
    const photoFileName = document.getElementById('photoFileName');
    const photoPreviewContainer = document.getElementById('photoPreviewContainer');
    
    photoInput.addEventListener('change', function() {
      if (this.files && this.files[0]) {
        const file = this.files[0];
        const reader = new FileReader();
        
        reader.onload = function(e) {
          photoPreview.src = e.target.result;
          photoFileName.textContent = file.name;
          photoPreviewContainer.style.display = 'block';
        }
        
        reader.readAsDataURL(file);
      }
    });
    
    // Video preview
    const videoInput = document.getElementById('{{ form.video.id_for_label }}');
    const videoPreview = document.getElementById('videoPreview');
    const videoFileName = document.getElementById('videoFileName');
    const videoPreviewContainer = document.getElementById('videoPreviewContainer');
    
    videoInput.addEventListener('change', function() {
      if (this.files && this.files[0]) {
        const file = this.files[0];
        const reader = new FileReader();
        
        reader.onload = function(e) {
          videoPreview.src = e.target.result;
          videoFileName.textContent = file.name;
          videoPreviewContainer.style.display = 'block';
        }
        
        reader.readAsDataURL(file);
      }
    });
    
    // Form validation
    const propertyForm = document.getElementById('propertyInquiryForm');
    
    propertyForm.addEventListener('submit', function(e) {
      let valid = true;
      
      // Validate photo
      if (photoInput.files.length === 0) {
        e.preventDefault();
        valid = false;
        
        // Create error message if not exists
        let errorList = photoInput.nextElementSibling;
        if (!errorList || !errorList.classList.contains('errorlist')) {
          errorList = document.createElement('ul');
          errorList.classList.add('errorlist');
          photoInput.parentNode.appendChild(errorList);
        }
        
        // Clear existing errors
        errorList.innerHTML = '';
        
        // Add new error
        const errorItem = document.createElement('li');
        errorItem.textContent = 'Property photo is required.';
        errorList.appendChild(errorItem);
      }
      
      return valid;
    });
  });
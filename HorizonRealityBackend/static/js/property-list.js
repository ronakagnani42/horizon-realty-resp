// Enhanced Property List Page JS - Complete Fixed Version
document.addEventListener('DOMContentLoaded', function() {
  
  // Initialize favorites functionality
  initFavorites();
  
  function initFavorites() {
    const favoriteButtons = document.querySelectorAll('.favorite-btn');
    
    // Check the status of each property and update UI accordingly
    favoriteButtons.forEach(button => {
        const propertyId = button.dataset.propertyId;
        
        // Only check status if user is logged in
        if (isUserLoggedIn()) {
            // Check if property is in favorites
            fetch(`/favorite-status/${propertyId}/`)
                .then(response => response.json())
                .then(data => {
                    updateFavoriteButtonState(button, data.is_favorite);
                })
                .catch(error => {
                    console.error('Error checking favorite status:', error);
                });
        }
        
        // Add click event listener
        button.addEventListener('click', handleFavoriteClick);
    });
  }

  // Function to update favorite button state consistently
  function updateFavoriteButtonState(button, isFavorite) {
    const icon = button.querySelector('i');
    
    if (isFavorite) {
        button.classList.add('active');
        if (icon) {
            // Remove all possible heart classes first
            icon.classList.remove('bi-heart', 'bi-heart-fill', 'far', 'fas', 'fa-heart');
            // Add filled heart class (using Bootstrap Icons)
            icon.classList.add('bi-heart-fill');
        }
    } else {
        button.classList.remove('active');
        if (icon) {
            // Remove all possible heart classes first
            icon.classList.remove('bi-heart', 'bi-heart-fill', 'far', 'fas', 'fa-heart');
            // Add empty heart class (using Bootstrap Icons)
            icon.classList.add('bi-heart');
        }
    }
  }

  // Function to handle favorite button clicks
  function handleFavoriteClick(event) {
    event.preventDefault();
    event.stopPropagation();
    
    const button = event.currentTarget;
    const propertyId = button.dataset.propertyId;
 
    // Send AJAX request to toggle favorite
    fetch(`/favorite/${propertyId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // If on favorites page and removing favorite, handle DOM removal
            if (!data.is_favorite && window.location.pathname.includes('my-favorites')) {
                const propertyCard = button.closest('.col-md-6');
                if (propertyCard) {
                    // Smooth removal animation
                    propertyCard.style.transition = 'opacity 0.5s ease';
                    propertyCard.style.opacity = '0';
                    
                    setTimeout(() => {
                        propertyCard.remove();
                        
                        // Update the count
                        const countElement = document.querySelector('.properties-found .count');
                        if (countElement) {
                            const currentCount = parseInt(countElement.textContent);
                            countElement.textContent = currentCount - 1;
                            
                            // Show "no results" if all favorites are removed
                            if (currentCount - 1 === 0) {
                                showNoFavoritesMessage();
                            }
                        }
                    }, 500);
                }
            } else {
                // Update the button state using our consistent function
                updateFavoriteButtonState(button, data.is_favorite);
                
                // Add animation for adding to favorites
                if (data.is_favorite) {
                    button.animate([
                        { transform: 'scale(1)' },
                        { transform: 'scale(1.3)' },
                        { transform: 'scale(1)' }
                    ], {
                        duration: 300,
                        iterations: 1
                    });
                    showToast('Property added to favorites!', 'success');
                } else {
                    showToast('Property removed from favorites', 'info');
                }
            }
        } else {
            showToast(data.message || 'Something went wrong. Please try again.', 'error');
        }
    })
    .catch(error => {
        console.error('Error toggling favorite:', error);
        showToast('Something went wrong. Please try again.', 'error');
    });
  }

  // Function to show "no favorites" message
  function showNoFavoritesMessage() {
    const propertiesContainer = document.getElementById('properties-container');
    const propertiesFound = document.querySelector('.properties-found');
    
    // Hide the container and properties found section
    if (propertiesContainer) propertiesContainer.style.display = 'none';
    if (propertiesFound) propertiesFound.style.display = 'none';
    
    // Create and display "no results" message
    const noResults = document.createElement('div');
    noResults.className = 'no-results';
    noResults.innerHTML = `
        <i class="bi bi-heart"></i>
        <h3>No Favorite Properties Yet</h3>
        <p>You haven't added any properties to your favorites list. Browse our properties and click the heart icon to add them here.</p>
        <a href="/properties/" class="btn-reset-filters">
            <i class="bi bi-search"></i> Browse Properties
        </a>
    `;
    
    // Add the no results message to the container
    const section = document.querySelector('.properties-section .container');
    if (section) section.appendChild(noResults);
  }

  // Function to check if user is logged in
  function isUserLoggedIn() {
    // Check for a specific element that only exists when logged in
    const authStatusElement = document.getElementById('user-authenticated');
    if (authStatusElement) {
        return authStatusElement.value === 'True';
    }
    
    // Or check if a specific user element exists (like a profile dropdown)
    const userProfileElement = document.querySelector('.user-profile-dropdown');
    return !!userProfileElement;
  }

  // Function to show toast notification
  function showToast(message, type = 'success') {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container';
        toastContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1050;
        `;
        document.body.appendChild(toastContainer);
    }
    
    // Create toast
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.style.cssText = `
        padding: 15px 20px;
        margin-bottom: 10px;
        border-radius: 8px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
        color: #fff;
        display: flex;
        align-items: center;
        justify-content: space-between;
        min-width: 300px;
        transform: translateX(120%);
        transition: transform 0.3s ease;
        background-color: ${getToastColor(type)};
    `;
    
    toast.innerHTML = `
        <div class="toast-content">
            <i class="bi ${getToastIcon(type)}"></i>
            <span style="margin-left: 10px;">${message}</span>
        </div>
        <i class="bi bi-x toast-close" style="cursor: pointer; margin-left: 15px;"></i>
    `;
    
    // Add to container
    toastContainer.appendChild(toast);
    
    // Show toast
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
    }, 10);
    
    // Add close button event
    const closeBtn = toast.querySelector('.toast-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            toast.style.transform = 'translateX(120%)';
            setTimeout(() => {
                toast.remove();
            }, 300);
        });
    }
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        toast.style.transform = 'translateX(120%)';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
  }

  function getToastColor(type) {
    switch(type) {
        case 'success': return '#28a745';
        case 'error': return '#dc3545';
        case 'warning': return '#ffc107';
        case 'info': return '#17a2b8';
        default: return '#17a2b8';
    }
  }

  function getToastIcon(type) {
    switch(type) {
        case 'success': return 'bi-check-circle';
        case 'error': return 'bi-exclamation-circle';
        case 'warning': return 'bi-exclamation-triangle';
        case 'info': return 'bi-info-circle';
        default: return 'bi-info-circle';
    }
  }

  // Function to get CSRF token
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }

  // Initialize any tooltips
  const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  if (tooltips.length > 0 && typeof bootstrap !== 'undefined') {
    tooltips.forEach(tooltip => {
      new bootstrap.Tooltip(tooltip);
    });
  }
  
  // Handle view toggle (grid vs list)
  const viewButtons = document.querySelectorAll('.view-btn');
  const propertyGrid = document.querySelector('.property-grid');
  
  viewButtons.forEach(button => {
    button.addEventListener('click', function() {
      // Remove active class from all buttons
      viewButtons.forEach(btn => btn.classList.remove('active'));
      
      // Add active class to clicked button
      this.classList.add('active');
      
      // Toggle grid/list view
      const viewType = this.getAttribute('data-view');
      
      if (propertyGrid) {
        // Get all property card containers
        const cardContainers = document.querySelectorAll('.property-grid > div, .property-list > div');
        
        if (viewType === 'list') {
          // Switch to list view
          propertyGrid.classList.remove('property-grid');
          propertyGrid.classList.add('property-list');
          
          // Adjust all card containers for list view
          cardContainers.forEach(container => {
            container.className = ''; // Clear all classes
            container.classList.add('col-12', 'mb-4'); // Add list view classes
            
            // Update the card layout for list view
            const card = container.querySelector('.property-card');
            if (card) {
              card.classList.add('d-md-flex', 'flex-md-row');
              
              // Adjust the image container width for list view
              const imageContainer = card.querySelector('.property-image');
              if (imageContainer) {
                imageContainer.classList.add('property-image-list');
                imageContainer.style.flex = '0 0 300px';
              }
              
              // Adjust details container for list view
              const detailsContainer = card.querySelector('.property-details');
              if (detailsContainer) {
                detailsContainer.classList.add('flex-grow-1', 'ps-md-3');
              }
            }
          });
        } else {
          // Switch to grid view
          propertyGrid.classList.remove('property-list');
          propertyGrid.classList.add('property-grid');
          
          // Reset all card containers for grid view
          cardContainers.forEach(container => {
            container.className = ''; // Clear all classes
            container.classList.add('col-md-6', 'col-lg-4', 'mb-4'); // Add grid view classes
            
            // Update the card layout for grid view
            const card = container.querySelector('.property-card');
            if (card) {
              card.classList.remove('d-md-flex', 'flex-md-row');
              
              // Reset image container for grid view
              const imageContainer = card.querySelector('.property-image');
              if (imageContainer) {
                imageContainer.classList.remove('property-image-list');
                imageContainer.style.flex = '';
              }
              
              // Reset details container for grid view
              const detailsContainer = card.querySelector('.property-details');
              if (detailsContainer) {
                detailsContainer.classList.remove('flex-grow-1', 'ps-md-3');
              }
            }
          });
        }
      }
      
      // Save preference in localStorage
      localStorage.setItem('propertyViewPreference', viewType);
    });
  });
  
  // Load view preference from localStorage on page load
  const savedViewPreference = localStorage.getItem('propertyViewPreference') || 'grid'; // Default to grid if not set
  const preferredViewButton = document.querySelector(`.view-btn[data-view="${savedViewPreference}"]`);
  if (preferredViewButton) {
    preferredViewButton.click(); // Trigger the click event to apply the saved view
  } else {
    // Fallback to first button if preferred view button not found
    const firstViewButton = document.querySelector('.view-btn');
    if (firstViewButton) {
      firstViewButton.click();
    }
  }
  
  // Handle form submission with current URL parameters
  const filterForm = document.querySelector('.filter-form');
  if (filterForm) {
    filterForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // Show loading state
      const submitBtn = this.querySelector('.filter-btn');
      const originalBtnText = submitBtn.innerHTML;
      submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Searching...`;
      submitBtn.disabled = true;
      
      // Get current URL parameters
      const urlParams = new URLSearchParams(window.location.search);
      
      // Create FormData from the form
      const formData = new FormData(filterForm);
      
      // Convert FormData to URLSearchParams
      const searchParams = new URLSearchParams();
      for (const [key, value] of formData.entries()) {
        if (value) { // Only add parameters with values
          searchParams.append(key, value);
        }
      }
      
      // Reset page to 1 when filtering
      searchParams.delete('page');
      
      // Redirect to the same page with new parameters
      setTimeout(() => {
        window.location.href = `${window.location.pathname}?${searchParams.toString()}`;
      }, 500); // Small delay for better UX
    });
  }
  
  // Handle inquiry button clicks
  const inquireButtons = document.querySelectorAll('.btn-inquire');
  inquireButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      const propertyId = this.getAttribute('data-property-id');
      
      // Get property title for the modal
      let propertyTitle = "Property Inquiry";
      const propertyCard = this.closest('.property-card');
      if (propertyCard) {
        const titleElement = propertyCard.querySelector('h3');
        if (titleElement) {
          propertyTitle = titleElement.textContent.trim();
        }
      }
      
      // Here you could open a modal or redirect to a contact form with the property ID
      if (typeof bootstrap !== 'undefined' && document.getElementById('inquiryModal')) {
        const inquiryModal = new bootstrap.Modal(document.getElementById('inquiryModal'));
        document.getElementById('inquiryPropertyId').value = propertyId;
        
        // Update modal title with property name
        const modalTitle = document.getElementById('inquiryModalLabel');
        if (modalTitle) {
          modalTitle.textContent = `Inquiry: ${propertyTitle}`;
        }
        
        inquiryModal.show();
      } else {
        // Fallback: redirect to contact page with property ID
        window.location.href = `/contact/?property_id=${propertyId}`;
      }
    });
  });
  
  // Handle inquiry form submission
  const inquiryForm = document.getElementById('inquiryForm');
  const submitInquiryBtn = document.getElementById('submitInquiry');
  
  if (inquiryForm && submitInquiryBtn) {
    submitInquiryBtn.addEventListener('click', function() {
      if (inquiryForm.checkValidity()) {
        // Show loading state
        const originalBtnText = submitInquiryBtn.textContent;
        submitInquiryBtn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Submitting...`;
        submitInquiryBtn.disabled = true;
        
        // Gather form data
        const formData = new FormData(inquiryForm);
        const formObject = {};
        formData.forEach((value, key) => {
          formObject[key] = value;
        });
        
        // Simulate form submission with fetch API
        fetch('/api/property-inquiry/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
          },
          body: JSON.stringify(formObject)
        })
        .then(response => response.json())
        .then(data => {
          // Close modal
          if (typeof bootstrap !== 'undefined') {
            const inquiryModal = bootstrap.Modal.getInstance(document.getElementById('inquiryModal'));
            inquiryModal.hide();
          }
          
          // Show success message
          showToast('Your inquiry has been submitted successfully! Our team will contact you soon.', 'success');
          
          // Reset form
          inquiryForm.reset();
        })
        .catch(error => {
          console.error('Error submitting inquiry:', error);
          showToast('There was an error submitting your inquiry. Please try again later.', 'error');
        })
        .finally(() => {
          // Reset button state
          submitInquiryBtn.innerHTML = originalBtnText;
          submitInquiryBtn.disabled = false;
        });
      } else {
        // Trigger HTML5 validation
        inquiryForm.reportValidity();
      }
    });
  }

  // Dynamic filter dependencies (e.g., show configuration only for residential)
  const propertyTypeSelect = document.getElementById('property_type');
  const configurationSelect = document.getElementById('configuration');
  const commercialTypeSelect = document.getElementById('commercial_type');
  
  if (propertyTypeSelect && configurationSelect) {
    propertyTypeSelect.addEventListener('change', function() {
      const selectedType = this.value;
      
      // Clear previous selections when changing property type
      configurationSelect.value = '';
      if (commercialTypeSelect) {
        commercialTypeSelect.value = '';
      }
      
      if (selectedType === 'residential') {
        // Show configuration for residential (1BHK, 2BHK, etc.)
        fadeIn(configurationSelect.closest('.col-md-6, .col-lg-3'));
        configurationSelect.disabled = false;
        
        // Hide commercial type
        if (commercialTypeSelect) {
          fadeOut(commercialTypeSelect.closest('.col-md-6, .col-lg-3'));
          commercialTypeSelect.disabled = true;
        }
        
        // Update configuration options for residential
        updateConfigurationOptions('residential');
        
      } else if (selectedType === 'commercial') {
        // Show configuration for commercial (if you have commercial configurations)
        fadeIn(configurationSelect.closest('.col-md-6, .col-lg-3'));
        configurationSelect.disabled = false;
        
        // Show commercial type if available
        if (commercialTypeSelect) {
          fadeIn(commercialTypeSelect.closest('.col-md-6, .col-lg-3'));
          commercialTypeSelect.disabled = false;
        }
        
        // Update configuration options for commercial
        updateConfigurationOptions('commercial');
        
      } else {
        // No property type selected - show both
        fadeIn(configurationSelect.closest('.col-md-6, .col-lg-3'));
        configurationSelect.disabled = false;
        
        if (commercialTypeSelect) {
          fadeIn(commercialTypeSelect.closest('.col-md-6, .col-lg-3'));
          commercialTypeSelect.disabled = false;
        }
        
        // Reset configuration options to show all
        updateConfigurationOptions('all');
      }
    });
    
    // Trigger change event on page load to set initial state
    propertyTypeSelect.dispatchEvent(new Event('change'));
  }
  
  
  // Budget range validation
  const minBudgetInput = document.getElementById('min_budget');
  const maxBudgetInput = document.getElementById('max_budget');
  
  if (minBudgetInput && maxBudgetInput) {
    minBudgetInput.addEventListener('change', validateBudget);
    maxBudgetInput.addEventListener('change', validateBudget);
    
    function validateBudget() {
      const minValue = parseInt(minBudgetInput.value) || 0;
      const maxValue = parseInt(maxBudgetInput.value) || Infinity;
      
      if (minValue > maxValue && maxValue !== 0) {
        // Set max value equal to min value if min exceeds max
        maxBudgetInput.value = minValue;
      }
    }
  }
  
  // Handle parallax effect on scroll
  window.addEventListener('scroll', function() {
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
      const scrollPosition = window.scrollY;
      heroSection.style.backgroundPositionY = `calc(50% + ${scrollPosition * 0.4}px)`;
    }
  });
  
  // AOS initialization for scroll animations
  if (typeof AOS !== 'undefined') {
    AOS.init({
      duration: 800,
      easing: 'ease-in-out',
      once: true,
      mirror: false
    });
  }
  
  // Helper Functions
  function showNotification(message, type = 'info') {
    // Use the same showToast function for consistency
    showToast(message, type);
  }
  
  function fadeIn(element) {
    if (!element) return;
    
    // Set initial state
    element.style.opacity = 0;
    element.style.display = 'block';
    
    // Animate to visible
    setTimeout(() => {
      element.style.transition = 'opacity 0.3s ease';
      element.style.opacity = 1;
    }, 10);
  }
  
  function fadeOut(element) {
    if (!element) return;
    
    // Animate to hidden
    element.style.transition = 'opacity 0.3s ease';
    element.style.opacity = 0;
    
    // Remove from DOM after animation
    setTimeout(() => {
      element.style.display = 'none';
    }, 300);
  }
});
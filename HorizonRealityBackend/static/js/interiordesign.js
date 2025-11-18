(function() {
    'use strict';
    
    // Check if script is already loaded to prevent double execution
    if (window.interiorDesignFormLoaded) {
        console.warn('Interior Design Form script already loaded');
        return;
    }
    window.interiorDesignFormLoaded = true;

    // Variables
    let form, termsCheckbox, downloadBtn;
    
    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        initializeForm();
        setupEventListeners();
        initializeUIEnhancements();
    });

    function initializeForm() {
        // Get form elements
        form = document.getElementById('interior-form');
        termsCheckbox = document.getElementById('terms-agreement');
        downloadBtn = document.getElementById('download-btn');
        
        // Activate the interior tab
        const interiorTab = document.getElementById('interior-tab');
        if (interiorTab) {
            interiorTab.classList.add('active');
        }
        
        // Show the interior form content
        const interiorContent = document.getElementById('interior');
        if (interiorContent) {
            interiorContent.classList.add('active');
            interiorContent.style.display = 'block';
        }

        // Initial state - button should be disabled
        setDownloadButtonState(false);
    }

    function setupEventListeners() {
        if (!form) return;

        // Form submission handling
        form.addEventListener('submit', handleFormSubmit);
        
        // Text inputs validation
        const textInputs = form.querySelectorAll('input[type="text"], input[type="tel"], input[type="number"]');
        textInputs.forEach(input => {
            input.addEventListener('input', updateDownloadButtonState);
            input.addEventListener('blur', updateDownloadButtonState);
            
            // Focus/blur animations
            input.addEventListener('focus', function() {
                this.parentNode.classList.add('focused');
            });
            
            input.addEventListener('blur', function() {
                if (!this.value) {
                    this.parentNode.classList.remove('focused');
                }
            });
            
            // Check if field has value on load
            if (input.value) {
                input.parentNode.classList.add('focused');
            }
        });
        
        // Radio buttons
        const radioInputs = form.querySelectorAll('input[type="radio"]');
        radioInputs.forEach(input => {
            input.addEventListener('change', function() {
                updateDownloadButtonState();
                handleRadioSelection(this);
            });
        });
        
        // Terms checkbox
        if (termsCheckbox) {
            termsCheckbox.addEventListener('change', updateDownloadButtonState);
        }

        // Phone input formatting
        const phoneInput = document.querySelector('input[name="phone_number"]');
        if (phoneInput) {
            phoneInput.addEventListener('input', formatPhoneInput);
        }

        // Area input validation
        const areaInput = document.querySelector('input[name="sqft"]');
        if (areaInput) {
            areaInput.addEventListener('input', validateAreaInput);
        }

        // Window events
        window.addEventListener('resize', debounce(handleWindowResize, 250));
        window.addEventListener('beforeunload', handleBeforeUnload);
    }

    function handleFormSubmit(e) {
        e.preventDefault();
        
        // Validate form before submission
        if (!validateForm()) {
            showToast('Please fill in all required fields and accept the terms.', 'error');
            return;
        }
        
        const phone = form.querySelector('input[name="phone_number"]').value.trim();
        
        // Validate phone number format
        if (!isValidPhone(phone)) {
            showToast('Please enter a valid phone number.', 'error');
            return;
        }
        
        // Show loading state
        const submitBtn = form.querySelector('.search-btn');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin" style="margin-right: 8px;"></i>Submitting...';
        submitBtn.disabled = true;
        
        // Submit form data using fetch API
        const formData = new FormData(form);
        
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => {
            // Check if response is JSON
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error('Server returned non-JSON response');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                showSuccessPopup();
                resetForm();
            } else {
                const message = data.message || 'An error occurred. Please try again.';
                showToast(message, 'error');
                
                // Handle specific field errors
                if (data.errors) {
                    handleFieldErrors(data.errors);
                }
            }
        })
        .catch(error => {
            console.error('Form submission error:', error);
            showToast('An error occurred. Please check your connection and try again.', 'error');
        })
        .finally(() => {
            // Restore submit button
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        });
    }

    function validateForm() {
        if (!form) return false;
        
        const name = form.querySelector('input[name="name"]').value.trim();
        const phone = form.querySelector('input[name="phone_number"]').value.trim();
        const propertyType = form.querySelector('input[name="property_types"]:checked');
        const serviceType = form.querySelector('input[name="service_types"]:checked');
        const termsAccepted = termsCheckbox && termsCheckbox.checked;
        
        return name && phone && propertyType && serviceType && termsAccepted;
    }

    function updateDownloadButtonState() {
        const isFormValid = validateForm();
        setDownloadButtonState(isFormValid);
    }

    function setDownloadButtonState(enabled) {
        if (!downloadBtn) return;
        
        downloadBtn.disabled = !enabled;
        if (enabled) {
            downloadBtn.style.opacity = '1';
            downloadBtn.style.cursor = 'pointer';
            downloadBtn.classList.remove('disabled');
        } else {
            downloadBtn.style.opacity = '0.6';
            downloadBtn.style.cursor = 'not-allowed';
            downloadBtn.classList.add('disabled');
        }
    }

    function handleRadioSelection(radio) {
        // Remove active class from all radio items in the same group
        const groupName = radio.name;
        const groupRadios = document.querySelectorAll(`input[name="${groupName}"]`);
        groupRadios.forEach(groupRadio => {
            groupRadio.closest('.radio-item').classList.remove('selected');
        });
        
        // Add active class to selected item
        radio.closest('.radio-item').classList.add('selected');
    }

    function formatPhoneInput(e) {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length > 10) {
            value = value.slice(0, 10);
        }
        e.target.value = value;
    }

    function validateAreaInput(e) {
        let value = e.target.value.replace(/[^\d]/g, '');
        if (value && parseInt(value) > 10000) {
            value = '10000'; // Set reasonable max limit
        }
        e.target.value = value;
    }

    function isValidPhone(phone) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
    }

    function resetForm() {
        if (!form) return;
        
        form.reset();
        setDownloadButtonState(false);
        
        // Reset radio buttons to default
        const defaultRadios = form.querySelectorAll('input[type="radio"][value="flat"], input[type="radio"][value="turnkey"]');
        defaultRadios.forEach(radio => radio.checked = true);
        
        // Remove focused classes
        const focusedGroups = form.querySelectorAll('.form-group.focused');
        focusedGroups.forEach(group => group.classList.remove('focused'));
        
        // Remove selected classes from radio items
        const selectedRadios = form.querySelectorAll('.radio-item.selected');
        selectedRadios.forEach(item => item.classList.remove('selected'));
    }

    function handleFieldErrors(errors) {
        Object.keys(errors).forEach(fieldName => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                field.style.borderColor = '#dc3545';
                field.addEventListener('input', function() {
                    this.style.borderColor = '';
                }, { once: true });
            }
        });
    }

    function handleWindowResize() {
        // Handle responsive adjustments if needed
        console.log('Window resized');
    }

    function handleBeforeUnload(e) {
        if (!form) return;
        
        const formData = new FormData(form);
        const hasData = Array.from(formData.values()).some(value => value.trim() !== '');
        
        if (hasData) {
            e.preventDefault();
            e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
            return e.returnValue;
        }
    }

    // Global functions that need to be accessible from HTML
    window.downloadPortfolio = function() {
        // Validate all required fields first
        if (!validateForm()) {
            const missingFields = [];
            
            const name = form.querySelector('input[name="name"]').value.trim();
            const phone = form.querySelector('input[name="phone_number"]').value.trim();
            const propertyType = form.querySelector('input[name="property_types"]:checked');
            const serviceType = form.querySelector('input[name="service_types"]:checked');
            const termsAccepted = termsCheckbox && termsCheckbox.checked;
            
            if (!name) {
                showToast('Please enter your full name to download the portfolio.', 'error');
                form.querySelector('input[name="name"]').focus();
                return;
            }
            
            if (!phone) {
                showToast('Please enter your phone number to download the portfolio.', 'error');
                form.querySelector('input[name="phone_number"]').focus();
                return;
            }
            
            if (!isValidPhone(phone)) {
                showToast('Please enter a valid phone number to download the portfolio.', 'error');
                form.querySelector('input[name="phone_number"]').focus();
                return;
            }
            
            if (!propertyType) {
                showToast('Please select a property type to download the portfolio.', 'error');
                return;
            }
            
            if (!serviceType) {
                showToast('Please select a service type to download the portfolio.', 'error');
                return;
            }
            
            if (!termsAccepted) {
                showToast('Please accept the terms and conditions to download the portfolio.', 'error');
                termsCheckbox.focus();
                return;
            }
        }
        
        // Get the brochure URL from the button's data attribute
        const brochureUrl = downloadBtn ? downloadBtn.getAttribute('data-url') : null;
        
        if (!brochureUrl) {
            showToast('Portfolio is not available at the moment. Please try again later.', 'error');
            return;
        }
        
        try {
            showToast('Starting download...', 'success');
            
            const originalText = downloadBtn.innerHTML;
            downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Downloading...';
            downloadBtn.disabled = true;
            
            // Create download link
            const link = document.createElement('a');
            link.href = brochureUrl;
            link.download = 'Horizon_Reality_Interior_Portfolio.pdf';
            link.target = '_blank';
            link.style.display = 'none';
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            setTimeout(() => {
                downloadBtn.innerHTML = originalText;
                downloadBtn.disabled = false;
                showToast('Portfolio download completed successfully!', 'success');
            }, 2000);
            
        } catch (error) {
            console.error('Download error:', error);
            showToast('Error downloading portfolio. Please try again.', 'error');
            
            if (downloadBtn) {
                downloadBtn.innerHTML = downloadBtn.getAttribute('data-original-text') || 'Download Portfolio';
                downloadBtn.disabled = false;
            }
        }
    };

    window.showSuccessPopup = function() {
        const popup = document.getElementById('successPopup');
        if (popup) {
            popup.classList.add('show');
            setTimeout(() => closePopup(), 10000);
        }
    };

    window.closePopup = function() {
        const popup = document.getElementById('successPopup');
        if (popup) {
            popup.classList.remove('show');
        }
    };

    window.openFilterTab = function(tabName) {
        // Hide all filter contents
        const filterContents = document.querySelectorAll('.filter-content');
        filterContents.forEach(content => {
            content.classList.remove('active');
            content.style.display = 'none';
        });
        
        // Remove active class from all tabs
        const filterTabs = document.querySelectorAll('.filter-tab');
        filterTabs.forEach(tab => {
            tab.classList.remove('active');
        });
        
        // Show selected tab content
        const selectedContent = document.getElementById(tabName);
        if (selectedContent) {
            selectedContent.style.display = 'block';
            setTimeout(() => {
                selectedContent.classList.add('active');
            }, 10);
        }
        
        // Add active class to selected tab
        const selectedTab = document.getElementById(tabName + '-tab');
        if (selectedTab) {
            selectedTab.classList.add('active');
        }
    };

    // Toast notification system
    function showToast(message, type = 'info', duration = 5000) {
        // Remove existing toasts
        const existingToasts = document.querySelectorAll('.toast-notification');
        existingToasts.forEach(toast => toast.remove());
        
        // Create toast container if it doesn't exist
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                max-width: 400px;
            `;
            document.body.appendChild(toastContainer);
        }
        
        // Create toast element
        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        
        const config = {
            'success': { bg: '#28a745', icon: 'fas fa-check-circle' },
            'error': { bg: '#dc3545', icon: 'fas fa-exclamation-triangle' },
            'info': { bg: '#17a2b8', icon: 'fas fa-info-circle' },
            'warning': { bg: '#ffc107', icon: 'fas fa-exclamation-circle' }
        };
        
        const { bg, icon } = config[type] || config.info;
        
        toast.style.cssText = `
            background: ${bg};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 14px;
            font-weight: 500;
            transform: translateX(100%);
            transition: all 0.3s ease;
            cursor: pointer;
        `;
        
        toast.innerHTML = `
            <div style="display: flex; align-items: center;">
                <i class="${icon}" style="margin-right: 10px; font-size: 16px;"></i>
                <span>${message}</span>
            </div>
            <button onclick="this.parentElement.remove()" style="
                background: none;
                border: none;
                color: white;
                font-size: 16px;
                cursor: pointer;
                padding: 0;
                margin-left: 15px;
                opacity: 0.8;
                transition: opacity 0.2s ease;
            ">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        toastContainer.appendChild(toast);
        
        // Animate in
        setTimeout(() => {
            toast.style.transform = 'translateX(0)';
        }, 10);
        
        // Auto remove
        setTimeout(() => {
            if (toast.parentNode) {
                toast.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    if (toast.parentNode) {
                        toast.remove();
                    }
                }, 300);
            }
        }, duration);
        
        // Click to dismiss
        toast.addEventListener('click', () => {
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.remove();
                }
            }, 300);
        });
    }

    function initializeUIEnhancements() {
        // Add ripple effect to buttons
        const buttons = document.querySelectorAll('.search-btn, .download-btn, .popup-close-btn');
        buttons.forEach(button => {
            button.addEventListener('click', function(e) {
                const ripple = document.createElement('span');
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.cssText = `
                    position: absolute;
                    width: ${size}px;
                    height: ${size}px;
                    left: ${x}px;
                    top: ${y}px;
                    background: rgba(255, 255, 255, 0.3);
                    border-radius: 50%;
                    transform: scale(0);
                    animation: ripple 0.6s linear;
                    pointer-events: none;
                `;
                
                this.style.position = 'relative';
                this.style.overflow = 'hidden';
                this.appendChild(ripple);
                
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });

        // Add enhanced CSS styles
        if (!document.getElementById('interior-form-styles')) {
            const style = document.createElement('style');
            style.id = 'interior-form-styles';
            style.textContent = `
                @keyframes ripple {
                    to {
                        transform: scale(4);
                        opacity: 0;
                    }
                }
                
                .form-group.focused .form-label {
                    color: var(--primary-color);
                    transform: translateY(-2px);
                }
                
                .radio-item.selected label {
                    animation: radioSelect 0.3s ease-out;
                }
                
                @keyframes radioSelect {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.05); }
                    100% { transform: scale(1); }
                }
                
                .toast-notification {
                    animation: slideInRight 0.3s ease-out;
                }
                
                @keyframes slideInRight {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
                
                .form-control:invalid {
                    border-color: #dc3545;
                }
                
                .form-control:valid {
                    border-color: #28a745;
                }
                
                .download-btn.disabled {
                    background-color: #d6d8db !important;
                    color: #6c757d !important;
                    cursor: not-allowed !important;
                    transform: none !important;
                    box-shadow: none !important;
                }
                
                .download-btn.disabled:hover {
                    background-color: #d6d8db !important;
                    transform: none !important;
                    box-shadow: none !important;
                }
            `;
            document.head.appendChild(style);
        }
    }

    // Utility functions
    function debounce(func, wait, immediate) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func(...args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func(...args);
        };
    }

    console.log('Interior Design Form JavaScript initialized successfully!');

})();
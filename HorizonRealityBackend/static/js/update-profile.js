document.addEventListener('DOMContentLoaded', function() {
    // Get profile data from hidden script tag
    const profileData = JSON.parse(document.getElementById('profile-data').textContent);
    
    const userTypeSelect = document.getElementById(profileData.form_user_type_id);
    const firmNameGroup = document.getElementById('firmNameGroup');
    const firmNameRequired = document.getElementById('firmNameRequired');
    const firmNameField = document.getElementById(profileData.form_firm_name_id);
    const form = document.getElementById('profileForm');
    const submitBtn = document.getElementById('submitBtn');
    
    // Check if updates are allowed (15-day restriction)
    let canUpdate = profileData.can_update;
    let daysRemaining = profileData.days_remaining;
    const RESTRICTION_DAYS = 15; // 15-day restriction period
    
    // Calculate real-time countdown
    function calculateRemainingTime() {
        // You'll need to pass the last_update timestamp from Django
        // For now, assuming you add last_update_timestamp to the JSON data
        if (profileData.last_update_timestamp && !canUpdate) {
            const lastUpdate = new Date(profileData.last_update_timestamp);
            const now = new Date();
            const timeDiff = now.getTime() - lastUpdate.getTime();
            const daysPassed = Math.floor(timeDiff / (1000 * 3600 * 24));
            const hoursInCurrentDay = Math.floor((timeDiff % (1000 * 3600 * 24)) / (1000 * 3600));
            
            const remainingDays = RESTRICTION_DAYS - daysPassed;
            const remainingHours = 24 - hoursInCurrentDay;
            
            return {
                days: Math.max(0, remainingDays),
                hours: remainingHours,
                totalHours: Math.max(0, (remainingDays * 24) + remainingHours)
            };
        }
        return { days: daysRemaining, hours: 0, totalHours: daysRemaining * 24 };
    }
    
    function toggleFirmNameRequirement() {
        if (userTypeSelect.value === 'broker') {
            firmNameRequired.style.display = 'inline';
            firmNameField.required = true;
            firmNameGroup.style.opacity = '1';
        } else {
            firmNameRequired.style.display = 'none';
            firmNameField.required = false;
            firmNameGroup.style.opacity = '0.7';
        }
    }
    
    // Initial check
    toggleFirmNameRequirement();
    
    // Listen for changes only if updates are allowed
    if (canUpdate) {
        userTypeSelect.addEventListener('change', toggleFirmNameRequirement);
    }
    
    // Handle form submission with AJAX
    if (canUpdate) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Show loading state
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Updating...';
            submitBtn.disabled = true;
            form.classList.add('loading');
            
            // Submit form via AJAX
            const formData = new FormData(form);
            
            fetch(form.action || window.location.pathname, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    showAlert('success', data.message || 'Profile updated successfully! You cannot update your profile again for 15 days.');
                    
                    // Activate 15-day restriction
                    disableForm();
                    
                    // Update local state with current timestamp
                    profileData.can_update = false;
                    profileData.days_remaining = RESTRICTION_DAYS;
                    profileData.last_update_timestamp = new Date().toISOString();
                    canUpdate = false;
                    
                    showRestrictionNotice();
                    startCountdown();
                    
                    // Optionally redirect after a delay
                    setTimeout(() => {
                        window.location.reload();
                    }, 3000);
                } else {
                    // Check if restriction is active
                    if (data.restriction_active) {
                        showAlert('warning', data.message || `Profile updates are restricted for ${data.days_remaining || daysRemaining} more days.`);
                        disableForm();
                        showRestrictionNotice();
                    } else {
                        // Show error messages
                        showAlert('danger', data.message || 'Failed to update profile. Please try again.');
                        
                        // Display field-specific errors
                        if (data.errors) {
                            for (const [field, errors] of Object.entries(data.errors)) {
                                const fieldName = field.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
                                showAlert('danger', `${fieldName}: ${errors.join(', ')}`);
                            }
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('danger', 'An error occurred while updating your profile. Please try again.');
            })
            .finally(() => {
                // Reset button state if not restricted
                if (canUpdate && profileData.can_update) {
                    submitBtn.innerHTML = '<i class="fas fa-save me-2"></i>Update Profile';
                    submitBtn.disabled = false;
                    form.classList.remove('loading');
                }
            });
        });
    } else {
        // If updates are not allowed, show restriction message on form submission attempt
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const timeRemaining = calculateRemainingTime();
            showAlert('warning', `You cannot update your profile for another ${timeRemaining.days} day${timeRemaining.days !== 1 ? 's' : ''} and ${timeRemaining.hours} hour${timeRemaining.hours !== 1 ? 's' : ''}. Profile updates are restricted for 15 days after each update.`);
        });
    }
    
    function disableForm() {
        // Disable all form inputs
        const inputs = form.querySelectorAll('input, select, textarea, button');
        inputs.forEach(input => {
            if (input.type !== 'hidden') {
                input.disabled = true;
                input.classList.add('disabled-field');
            }
        });
        
        // Add visual indication
        form.classList.add('form-disabled');
        
        // Update button text
        submitBtn.innerHTML = '<i class="fas fa-lock me-2"></i>Update Restricted';
        submitBtn.classList.add('btn-secondary');
        submitBtn.classList.remove('btn-primary');
    }
    
    function showRestrictionNotice() {
        // Remove existing restriction notice if any
        const existingNotice = document.querySelector('.restriction-notice');
        if (existingNotice) {
            existingNotice.remove();
        }
        
        const timeRemaining = calculateRemainingTime();
        
        // Create new restriction notice
        const restrictionNotice = document.createElement('div');
        restrictionNotice.className = 'restriction-notice alert alert-warning border-left-warning';
        restrictionNotice.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="icon me-3">
                    <i class="fas fa-clock fa-2x text-warning"></i>
                </div>
                <div>
                    <h5 class="mb-1">Profile Update Restricted</h5>
                    <p class="mb-1">You cannot update your profile for another <strong><span class="countdown-timer">${timeRemaining.days} day${timeRemaining.days !== 1 ? 's' : ''} and ${timeRemaining.hours} hour${timeRemaining.hours !== 1 ? 's' : ''}</span></strong>.</p>
                    <small class="text-muted">Profile updates are limited to once every 15 days to maintain data integrity.</small>
                </div>
            </div>
            <div class="progress mt-2" style="height: 6px;">
                <div class="progress-bar bg-warning" role="progressbar" style="width: ${((RESTRICTION_DAYS * 24 - timeRemaining.totalHours) / (RESTRICTION_DAYS * 24)) * 100}%"></div>
            </div>
        `;
        
        // Insert after profile header
        const profileHeader = document.querySelector('.profile-header');
        if (profileHeader) {
            profileHeader.insertAdjacentElement('afterend', restrictionNotice);
        } else {
            // Fallback: insert at top of form
            const formSection = document.querySelector('.form-section') || form;
            formSection.insertBefore(restrictionNotice, formSection.firstChild);
        }
    }
    
    function updateCountdownDisplay() {
        const countdownElement = document.querySelector('.countdown-timer');
        const progressBar = document.querySelector('.restriction-notice .progress-bar');
        
        if (countdownElement && !canUpdate) {
            const timeRemaining = calculateRemainingTime();
            
            // Check if restriction period is over
            if (timeRemaining.days <= 0 && timeRemaining.hours <= 0) {
                // Enable the form and refresh the page
                canUpdate = true;
                profileData.can_update = true;
                window.location.reload();
                return;
            }
            
            // Update countdown text
            countdownElement.textContent = `${timeRemaining.days} day${timeRemaining.days !== 1 ? 's' : ''} and ${timeRemaining.hours} hour${timeRemaining.hours !== 1 ? 's' : ''}`;
            
            // Update progress bar
            if (progressBar) {
                const percentage = ((RESTRICTION_DAYS * 24 - timeRemaining.totalHours) / (RESTRICTION_DAYS * 24)) * 100;
                progressBar.style.width = `${Math.min(100, Math.max(0, percentage))}%`;
            }
        }
    }
    
    function startCountdown() {
        // Update every minute for more accurate countdown
        const countdownInterval = setInterval(() => {
            updateCountdownDisplay();
            
            // Check if we should stop the countdown
            const timeRemaining = calculateRemainingTime();
            if (timeRemaining.days <= 0 && timeRemaining.hours <= 0) {
                clearInterval(countdownInterval);
            }
        }, 60000); // Update every minute
        
        // Initial update
        updateCountdownDisplay();
    }
    
    function showAlert(type, message) {
        // Remove existing alerts of the same type
        const existingAlerts = document.querySelectorAll(`.alert-${type}`);
        existingAlerts.forEach(alert => {
            if (!alert.classList.contains('restriction-notice')) {
                alert.remove();
            }
        });
        
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            <i class="fas fa-${getAlertIcon(type)} me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Insert at the top of the form section or after restriction notice
        const restrictionNotice = document.querySelector('.restriction-notice');
        const formSection = document.querySelector('.form-section') || form;
        
        if (restrictionNotice && type !== 'warning') {
            restrictionNotice.insertAdjacentElement('afterend', alertDiv);
        } else {
            formSection.insertBefore(alertDiv, formSection.firstChild);
        }
        
        // Auto-dismiss after 5 seconds for non-error messages
        if (type !== 'danger') {
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.classList.remove('show');
                    setTimeout(() => alertDiv.remove(), 150);
                }
            }, 5000);
        }
    }
    
    function getAlertIcon(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'exclamation-triangle',
            'warning': 'exclamation-circle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    // Disable form interactions if updates are not allowed
    if (!canUpdate) {
        // Disable all form controls
        const formControls = form.querySelectorAll('input:not([type="hidden"]), select, textarea');
        formControls.forEach(control => {
            control.disabled = true;
            control.classList.add('disabled-field');
        });
        
        // Show restriction notice on page load and start countdown
        showRestrictionNotice();
        disableForm();
        startCountdown();
        
        // Add visual feedback on interaction attempts
        form.addEventListener('click', function(e) {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') {
                const timeRemaining = calculateRemainingTime();
                showAlert('info', `Profile updates are restricted for ${timeRemaining.days} more day${timeRemaining.days !== 1 ? 's' : ''} and ${timeRemaining.hours} hour${timeRemaining.hours !== 1 ? 's' : ''}. You can update your profile once every 15 days.`);
            }
        });
        
        // Prevent form interactions
        form.addEventListener('focus', function(e) {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') {
                e.target.blur();
            }
        }, true);
    }
});
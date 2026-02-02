// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function () {
    initializeLoginPage();
    initializeGoogleSignIn();
});

function initializeLoginPage() {
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize login button loading state
    initializeLoginButton();
    
    // Auto-focus first input
    const firstInput = document.querySelector('input[type="email"]');
    if (firstInput) {
        firstInput.focus();
    }
    
    // Check if modal exists
    const modal = document.getElementById('resetModal');
    if (!modal) {
        console.error('Reset modal element not found in DOM');
    }
}

// ================================
// ADDED: Google Sign-In Handler
// ================================
function initializeGoogleSignIn() {
    const googleSigninBtn = document.getElementById('google-signin-btn');
    
    if (googleSigninBtn) {
        googleSigninBtn.addEventListener('click', handleGoogleSignIn);
    }
}

/**
 * Handle Google Sign-In button click
 * Redirects to django-allauth Google OAuth URL
 */
function handleGoogleSignIn(e) {
    e.preventDefault();
    
    const btn = e.currentTarget;
    const btnText = btn.querySelector('.google-btn-text');
    const originalText = btnText.textContent;
    
    // Show loading state
    btn.classList.add('loading');
    btn.disabled = true;
    btnText.textContent = 'Redirecting to Google...';
    
    // Redirect to Google OAuth (handled by django-allauth)
    window.location.href = '/accounts/google/login/';
}

// Password toggle functionality
function togglePassword(fieldId) {
    const field = document.getElementById(fieldId);
    if (!field) {
        console.error('Password field not found:', fieldId);
        return;
    }
    
    const toggleBtn = field.parentElement.querySelector('.toggle-password');
    if (!toggleBtn) {
        console.error('Toggle button not found');
        return;
    }
    
    const icon = toggleBtn.querySelector('i');
    if (!icon) {
        console.error('Icon not found');
        return;
    }

    if (field.type === 'password') {
        field.type = 'text';
        icon.className = 'fas fa-eye-slash';
    } else {
        field.type = 'password';
        icon.className = 'fas fa-eye';
    }
}

// Modal functionality
function openResetModal() {
    const modal = document.getElementById('resetModal');
    if (!modal) {
        console.error('Reset modal not found');
        alert('Unable to open password reset form. Please refresh the page and try again.');
        return;
    }
    
    modal.style.display = 'flex';
    // Force reflow before adding class for animation
    modal.offsetHeight;
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
    
    // Focus on email input
    setTimeout(() => {
        const emailInput = document.getElementById('resetEmail');
        if (emailInput) {
            emailInput.focus();
        }
    }, 100);
}

function closeResetModal() {
    const modal = document.getElementById('resetModal');
    if (!modal) return;
    
    modal.classList.remove('show');
    // Wait for animation before hiding
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300);
    document.body.style.overflow = 'auto';
    
    // Reset form and hide messages
    const form = document.getElementById('resetPasswordForm');
    if (form) form.reset();
    
    const successMsg = document.getElementById('resetSuccess');
    if (successMsg) successMsg.style.display = 'none';
    
    const errorMsg = document.getElementById('resetError');
    if (errorMsg) errorMsg.style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function (event) {
    const modal = document.getElementById('resetModal');
    if (modal && event.target === modal) {
        closeResetModal();
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function (e) {
    // Close modal with Escape key
    if (e.key === 'Escape') {
        const modal = document.getElementById('resetModal');
        if (modal && modal.classList.contains('show')) {
            closeResetModal();
        }
    }

    // Submit form with Ctrl+Enter
    if (e.ctrlKey && e.key === 'Enter') {
        const form = document.querySelector('form[action*="login"]');
        if (form) {
            form.requestSubmit();
        }
    }
});

// Form validation functions
function initializeFormValidation() {
    const form = document.querySelector('form[action*="login"]');
    if (!form) return;

    const inputs = form.querySelectorAll('input[required]');

    inputs.forEach(input => {
        input.addEventListener('blur', function () {
            validateField(this);
        });

        input.addEventListener('input', function () {
            clearErrors(this);
        });
    });

    form.addEventListener('submit', function (e) {
        let isValid = true;
        inputs.forEach(input => {
            if (!validateField(input)) {
                isValid = false;
            }
        });

        if (!isValid) {
            e.preventDefault();
        }
    });
}

function validateField(field) {
    const value = field.value.trim();
    let isValid = true;

    // Clear previous errors
    clearErrors(field);

    if (field.type === 'email') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showError(field, 'Please enter a valid email address');
            isValid = false;
        }
    }

    if (field.type === 'password' && field.name !== 'email') {
        if (value.length < 6) {
            showError(field, 'Password must be at least 6 characters long');
            isValid = false;
        }
    }

    if (field.required && !value) {
        showError(field, 'This field is required');
        isValid = false;
    }

    return isValid;
}

function showError(field, message) {
    const formGroup = field.closest('.form-group');
    if (!formGroup) return;
    
    let errorDiv = formGroup.querySelector('.error-message:not([data-server-error])');

    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        formGroup.appendChild(errorDiv);
    }

    errorDiv.textContent = message;
    field.style.borderColor = '#ff6b6b';
}

function clearErrors(field) {
    const formGroup = field.closest('.form-group');
    if (!formGroup) return;
    
    const errorDivs = formGroup.querySelectorAll('.error-message:not([data-server-error])');
    errorDivs.forEach(div => div.remove());

    field.style.borderColor = '';
}

// Loading state for login button
function initializeLoginButton() {
    const loginForm = document.querySelector('form[action*="login"]');
    if (!loginForm) return;
    
    loginForm.addEventListener('submit', function (e) {
        const button = this.querySelector('.login-button');
        if (!button) return;
        
        // Only show loading if form is valid
        const isValid = loginForm.checkValidity();
        if (!isValid) return;
        
        const originalText = button.textContent;

        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Signing In...';
        button.disabled = true;

        // Re-enable button after 5 seconds (in case of error)
        setTimeout(() => {
            button.textContent = originalText;
            button.disabled = false;
        }, 5000);
    });
}

// Handle password reset form submission (optional AJAX)
document.addEventListener('DOMContentLoaded', function() {
    const resetForm = document.getElementById('resetPasswordForm');
    if (!resetForm) return;
    
    resetForm.addEventListener('submit', function(e) {
        const submitBtn = document.getElementById('resetSubmitBtn');
        const email = document.getElementById('resetEmail').value;
        
        if (!email) {
            e.preventDefault();
            alert('Please enter your email address');
            return;
        }
        
        // Show loading state
        if (submitBtn) {
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
            submitBtn.disabled = true;
        }
        
        // Form will submit normally to Django backend
        // If you want AJAX submission, prevent default and use fetch here
    });
});
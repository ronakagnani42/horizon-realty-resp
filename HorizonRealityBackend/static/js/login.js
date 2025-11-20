// Password toggle functionality
function togglePassword(fieldId) {
    const field = document.getElementById(fieldId);
    const icon = field.nextElementSibling.querySelector('i');

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
    document.getElementById('resetModal').classList.add('show');
    document.body.style.overflow = 'hidden';
}

function closeResetModal() {
    document.getElementById('resetModal').classList.remove('show');
    document.body.style.overflow = 'auto';
    // Reset form and hide success message
    const form = document.getElementById('resetPasswordForm');
    if (form) form.reset();
    document.getElementById('resetSuccess').style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function (event) {
    const modal = document.getElementById('resetModal');
    if (event.target === modal) {
        closeResetModal();
    }
}

// Enhanced form validation
document.addEventListener('DOMContentLoaded', function () {
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
});

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

    if (field.type === 'password') {
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
    let errorDiv = formGroup.querySelector('.error-message');

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
    const errorDiv = formGroup.querySelector('.error-message');

    if (errorDiv && !errorDiv.hasAttribute('data-server-error')) {
        errorDiv.remove();
    }

    field.style.borderColor = '';
}

// Loading state for login button
const loginForm = document.querySelector('form[action*="login"]');
if (loginForm) {
    loginForm.addEventListener('submit', function () {
        const button = this.querySelector('.login-button');
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

// Keyboard shortcuts
document.addEventListener('keydown', function (e) {
    // Close modal with Escape key
    if (e.key === 'Escape') {
        closeResetModal();
    }

    // Submit form with Ctrl+Enter
    if (e.ctrlKey && e.key === 'Enter') {
        const form = document.querySelector('form[action*="login"]');
        if (form) {
            form.submit();
        }
    }
});

// Auto-focus first input
window.addEventListener('load', function () {
    const firstInput = document.querySelector('input[type="email"]');
    if (firstInput) {
        firstInput.focus();
    }
});
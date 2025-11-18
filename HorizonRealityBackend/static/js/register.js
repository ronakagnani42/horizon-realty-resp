document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('registration-form');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm_password');
    const registerBtn = document.getElementById('register-btn');
    const userType = document.getElementById('user_type');
    const firmType = document.getElementById('firm_type');
    const firmTypeContainer = document.getElementById('firm_type_container');
    const firmNameContainer = document.getElementById('firm_name_container');
    const accountTypeRow = document.getElementById('account-type-row');

    // Handle user type change
    userType.addEventListener('change', function () {
        if (this.value === 'broker') {
            firmTypeContainer.classList.remove('hidden');
            firmTypeContainer.classList.add('visible');
            accountTypeRow.classList.add('two-columns');
        } else {
            firmTypeContainer.classList.add('hidden');
            firmTypeContainer.classList.remove('visible');
            firmNameContainer.classList.add('hidden');
            firmNameContainer.classList.remove('visible');
            accountTypeRow.classList.remove('two-columns');
        }
    });

    // Handle firm type change
    firmType.addEventListener('change', function () {
        if (this.value === 'firm') {
            firmNameContainer.classList.remove('hidden');
            firmNameContainer.classList.add('visible');
        } else {
            firmNameContainer.classList.add('hidden');
            firmNameContainer.classList.remove('visible');
        }
    });

    // Password strength checker
    password.addEventListener('input', function () {
        checkPasswordStrength(this.value);
        validatePasswordMatch();
    });

    confirmPassword.addEventListener('input', validatePasswordMatch);

    // Form submission
    form.addEventListener('submit', function (e) {
        e.preventDefault();
        if (validateForm()) {
            submitForm();
        }
    });

    // Real-time validation
    const inputs = form.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('blur', function () {
            validateField(this);
        });

        input.addEventListener('input', function () {
            clearError(this.name);
        });
    });
});

function togglePassword(fieldId, icon) {
    const field = document.getElementById(fieldId);
    const isPassword = field.type === 'password';

    field.type = isPassword ? 'text' : 'password';
    icon.className = isPassword ? 'fas fa-eye-slash toggle-password' : 'fas fa-eye toggle-password';
}

function checkPasswordStrength(password) {
    const meter = document.getElementById('strength-meter');
    const text = document.getElementById('strength-text');

    const requirements = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        number: /\d/.test(password),
        special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
    };

    // Update requirement indicators
    updateRequirement('length-req', requirements.length);
    updateRequirement('uppercase-req', requirements.uppercase);
    updateRequirement('lowercase-req', requirements.lowercase);
    updateRequirement('number-req', requirements.number);
    updateRequirement('special-req', requirements.special);

    // Calculate strength
    const validCount = Object.values(requirements).filter(Boolean).length;
    let strength = 'weak';

    if (validCount >= 5) strength = 'strong';
    else if (validCount >= 4) strength = 'good';
    else if (validCount >= 2) strength = 'fair';

    meter.className = `strength-meter ${strength}`;
    text.className = `strength-text ${strength}`;
    text.textContent = strength.toUpperCase();
}

function updateRequirement(id, isValid) {
    const req = document.getElementById(id);
    const icon = req.querySelector('i');

    if (isValid) {
        req.classList.add('valid');
        icon.className = 'fas fa-check-circle valid';
    } else {
        req.classList.remove('valid');
        icon.className = 'fas fa-circle invalid';
    }
}

function validatePasswordMatch() {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;

    if (confirmPassword && password !== confirmPassword) {
        showError('confirm_password', 'Passwords do not match');
        return false;
    } else {
        clearError('confirm_password');
        return true;
    }
}

function validateField(field) {
    const value = field.value.trim();
    const name = field.name;

    switch (name) {
        case 'first_name':
        case 'last_name':
            if (!value) {
                showError(name, 'This field is required');
                return false;
            } else if (value.length < 2) {
                showError(name, 'Name must be at least 2 characters');
                return false;
            }
            break;

        case 'email':
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!value) {
                showError(name, 'Email is required');
                return false;
            } else if (!emailRegex.test(value)) {
                showError(name, 'Please enter a valid email address');
                return false;
            }
            break;

        case 'contact_number':
            const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
            if (!value) {
                showError(name, 'Phone number is required');
                return false;
            } else if (!phoneRegex.test(value.replace(/[\s\-\(\)]/g, ''))) {
                showError(name, 'Please enter a valid phone number');
                return false;
            }
            break;

        case 'user_type':
            if (!value) {
                showError(name, 'Please select an account type');
                return false;
            }
            break;

        case 'password':
            if (!value) {
                showError(name, 'Password is required');
                return false;
            } else if (value.length < 8) {
                showError(name, 'Password must be at least 8 characters');
                return false;
            }
            break;
    }

    clearError(name);
    return true;
}

function validateForm() {
    const fields = ['first_name', 'last_name', 'email', 'contact_number', 'user_type', 'password'];
    let isValid = true;

    fields.forEach(fieldName => {
        const field = document.getElementById(fieldName);
        if (!validateField(field)) {
            isValid = false;
        }
    });

    // Check password match
    if (!validatePasswordMatch()) {
        isValid = false;
    }

    // Check terms agreement
    const terms = document.getElementById('terms');
    if (!terms.checked) {
        showNotification('error-notification', 'Please accept the Terms of Service');
        isValid = false;
    }

    return isValid;
}

function submitForm() {
    const btn = document.getElementById('register-btn');
    const btnText = btn.querySelector('.button-text');
    const spinner = document.getElementById('loading-spinner');

    // Show loading state
    btn.disabled = true;
    btnText.style.display = 'none';
    spinner.style.display = 'inline-block';

    // Simulate form submission
    setTimeout(() => {
        // Reset button state
        btn.disabled = false;
        btnText.style.display = 'inline-block';
        spinner.style.display = 'none';

        // Show success notification
        showNotification('success-notification');

        // Reset form
        document.getElementById('registration-form').reset();

        // Reset password strength indicators
        const meter = document.getElementById('strength-meter');
        const text = document.getElementById('strength-text');
        meter.className = 'strength-meter';
        text.className = 'strength-text';
        text.textContent = '';

        // Reset all requirements
        const requirements = document.querySelectorAll('.requirement');
        requirements.forEach(req => {
            req.classList.remove('valid');
            const icon = req.querySelector('i');
            icon.className = 'fas fa-circle invalid';
        });

        // Hide conditional fields
        const firmTypeContainer = document.getElementById('firm_type_container');
        const firmNameContainer = document.getElementById('firm_name_container');
        const accountTypeRow = document.getElementById('account-type-row');

        firmTypeContainer.classList.add('hidden');
        firmTypeContainer.classList.remove('visible');
        firmNameContainer.classList.add('hidden');
        firmNameContainer.classList.remove('visible');
        accountTypeRow.classList.remove('two-columns');

    }, 2000);
}

function showError(fieldName, message) {
    const errorDiv = document.getElementById(fieldName + '_error');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'flex';
    }
}

function clearError(fieldName) {
    const errorDiv = document.getElementById(fieldName + '_error');
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
}

function showNotification(id, customMessage = null) {
    const notification = document.getElementById(id);
    if (customMessage) {
        const messageElement = notification.querySelector('.notification-message');
        messageElement.textContent = customMessage;
    }

    notification.style.display = 'block';
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);

    // Auto hide after 5 seconds
    setTimeout(() => {
        hideNotification(id);
    }, 5000);
}

function hideNotification(id) {
    const notification = document.getElementById(id);
    notification.classList.remove('show');
    setTimeout(() => {
        notification.style.display = 'none';
    }, 400);
}

// Add some interactive effects
document.addEventListener('mousemove', function (e) {
    const particles = document.querySelectorAll('.particle');
    const mouseX = e.clientX / window.innerWidth;
    const mouseY = e.clientY / window.innerHeight;

    particles.forEach((particle, index) => {
        const speed = (index + 1) * 0.5;
        const x = mouseX * speed;
        const y = mouseY * speed;

        particle.style.transform = `translate(${x}px, ${y}px)`;
    });
});
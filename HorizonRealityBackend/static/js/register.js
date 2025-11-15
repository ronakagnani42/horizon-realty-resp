// Email validation function
function validateEmail(email) {
    const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

// Contact number validation function
function validateContactNumber(number) {
    const cleanNumber = number.replace(/\D/g, '');
    return cleanNumber.length === 10;
}

// Initialize form elements and event listeners
document.addEventListener('DOMContentLoaded', function() {
    const emailInput = document.getElementById('email');
    const emailError = document.getElementById('emailError');
    const contactInput = document.getElementById('contact_number');
    const contactError = document.createElement('div');
    contactError.id = 'contactError';
    contactError.className = 'error-message';
    contactError.textContent = 'Please enter a valid 10-digit phone number';
    contactError.style.display = 'none';

    if (contactInput && contactInput.parentElement) {
        contactInput.parentElement.after(contactError);
    }

    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    const confirmPasswordError = document.getElementById('confirm_password_error');
    const passwordStrengthMeter = document.getElementById('strength-meter');
    const passwordStrengthText = document.getElementById('strength-text');

    const lengthRequirement = document.getElementById('length-req');
    const lowercaseRequirement = document.getElementById('lowercase-req');
    const uppercaseRequirement = document.getElementById('uppercase-req');
    const numberRequirement = document.getElementById('number-req');
    const specialRequirement = document.getElementById('special-req');

    // Email validation
    if (emailInput && emailError) {
        emailInput.addEventListener('input', function () {
            const email = this.value.trim();
            if (email === '') {
                emailInput.classList.remove('valid-email', 'invalid-email');
                emailError.style.display = 'none';
                return;
            }
            if (validateEmail(email)) {
                emailInput.classList.add('valid-email');
                emailInput.classList.remove('invalid-email');
                emailError.style.display = 'none';
            } else {
                emailInput.classList.add('invalid-email');
                emailInput.classList.remove('valid-email');
                emailError.style.display = 'block';
            }
        });

        emailInput.addEventListener('blur', function () {
            const email = this.value.trim();
            if (email !== '' && !validateEmail(email)) {
                emailError.style.display = 'block';
            }
        });
    }

    // Contact number validation
    if (contactInput && contactError) {
        contactInput.addEventListener('input', function () {
            let digits = this.value.replace(/\D/g, '').slice(0, 10);
            this.value = digits;

            if (digits === '') {
                contactInput.classList.remove('valid-contact', 'invalid-contact');
                contactError.style.display = 'none';
                return;
            }
            if (validateContactNumber(digits)) {
                contactInput.classList.add('valid-contact');
                contactInput.classList.remove('invalid-contact');
                contactError.style.display = 'none';
            } else {
                contactInput.classList.add('invalid-contact');
                contactInput.classList.remove('valid-contact');
                contactError.style.display = 'block';
            }
        });

        contactInput.addEventListener('paste', function (e) {
            let pastedText = (e.clipboardData || window.clipboardData).getData('text');
            const cleanDigits = pastedText.replace(/\D/g, '').slice(0, 10);
            e.preventDefault();
            this.value = cleanDigits;
            const event = new Event('input');
            this.dispatchEvent(event);
        });

        contactInput.addEventListener('blur', function () {
            const contactNumber = this.value.trim();
            if (contactNumber !== '' && !validateContactNumber(contactNumber)) {
                contactError.style.display = 'block';
            }
        });
    }

    // Password validation
    function validatePassword(password) {
        if (!passwordInput || !passwordStrengthMeter || !passwordStrengthText) {
            console.error('Password validation elements not found');
            return false;
        }

        const hasLength = password.length >= 8;
        const hasLowercase = /[a-z]/.test(password);
        const hasUppercase = /[A-Z]/.test(password);
        const hasNumber = /[0-9]/.test(password);
        const hasSpecial = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);

        updateRequirement(lengthRequirement, hasLength);
        updateRequirement(lowercaseRequirement, hasLowercase);
        updateRequirement(uppercaseRequirement, hasUppercase);
        updateRequirement(numberRequirement, hasNumber);
        updateRequirement(specialRequirement, hasSpecial);

        let strength = 0;
        if (hasLength) strength += 20;
        if (hasLowercase) strength += 20;
        if (hasUppercase) strength += 20;
        if (hasNumber) strength += 20;
        if (hasSpecial) strength += 20;

        passwordStrengthMeter.style.width = strength + '%';
        passwordStrengthMeter.className = '';
        passwordStrengthText.style.color = '';

        if (strength <= 40) {
            passwordStrengthMeter.classList.add('strength-weak');
            passwordStrengthText.textContent = 'Weak';
            passwordStrengthText.style.color = '#dc3545';
        } else if (strength <= 60) {
            passwordStrengthMeter.classList.add('strength-medium');
            passwordStrengthText.textContent = 'Medium';
            passwordStrengthText.style.color = '#ffc107';
        } else if (strength <= 80) {
            passwordStrengthMeter.classList.add('strength-strong');
            passwordStrengthText.textContent = 'Strong';
            passwordStrengthText.style.color = '#28a745';
        } else {
            passwordStrengthMeter.classList.add('strength-very-strong');
            passwordStrengthText.textContent = 'Very Strong';
            passwordStrengthText.style.color = '#38b000';
        }

        if (strength >= 60) {
            passwordInput.classList.add('valid-password');
            passwordInput.classList.remove('invalid-password');
            return true;
        } else if (password.length > 0) {
            passwordInput.classList.add('invalid-password');
            passwordInput.classList.remove('valid-password');
            return false;
        } else {
            passwordInput.classList.remove('valid-password', 'invalid-password');
            return false;
        }
    }

    function updateRequirement(element, isValid) {
        if (!element) return;
        const icon = element.querySelector('i');
        if (!icon) return;

        if (isValid) {
            icon.classList.remove('fa-circle', 'invalid');
            icon.classList.add('fa-check-circle', 'valid');
            element.classList.add('valid');
            element.classList.remove('invalid');
        } else {
            icon.classList.remove('fa-check-circle', 'valid');
            icon.classList.add('fa-circle', 'invalid');
            element.classList.add('invalid');
            element.classList.remove('valid');
        }
    }

    // Password match validation
    function validatePasswordMatch() {
        if (!confirmPasswordInput || !confirmPasswordError) return false;
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        if (confirmPassword.length === 0) {
            confirmPasswordInput.classList.remove('valid-password', 'invalid-password');
            confirmPasswordError.style.display = 'none';
            return false;
        }

        if (password === confirmPassword) {
            confirmPasswordInput.classList.add('valid-password');
            confirmPasswordInput.classList.remove('invalid-password');
            confirmPasswordError.style.display = 'none';
            return true;
        } else {
            confirmPasswordInput.classList.add('invalid-password');
            confirmPasswordInput.classList.remove('valid-password');
            confirmPasswordError.style.display = 'block';
            return false;
        }
    }

    // Event listeners for passwords
    if (passwordInput) {
        passwordInput.addEventListener('input', function () {
            validatePassword(this.value);
            if (confirmPasswordInput.value.length > 0) {
                validatePasswordMatch();
            }
        });
    }

    if (confirmPasswordInput) {
        confirmPasswordInput.addEventListener('input', validatePasswordMatch);
    }

    // Conditional field logic
    function initializeConditionalFields() {
        const userTypeSelect = document.getElementById('user_type');
        const firmTypeSelect = document.getElementById('firm_type');
        const firmTypeContainer = document.getElementById('firm_type_container');
        const firmNameContainer = document.getElementById('firm_name_container');
        const firmNameInput = document.getElementById('firm_name');
        const conditionalRow = firmTypeContainer ? firmTypeContainer.closest('.form-row.conditional') : null;

        if (!userTypeSelect || !firmTypeSelect || !firmTypeContainer || !firmNameContainer || !firmNameInput || !conditionalRow) return;

        function updateFieldVisibility() {
            if (userTypeSelect.value === 'broker') {
                firmTypeContainer.classList.remove('hidden');
                firmTypeContainer.classList.add('visible');
                firmTypeSelect.required = true;
                conditionalRow.classList.add('two-columns');

                if (firmTypeSelect.value === 'firm') {
                    firmNameContainer.classList.remove('hidden');
                    firmNameContainer.classList.add('visible');
                    firmNameInput.required = true;
                } else {
                    firmNameContainer.classList.add('hidden');
                    firmNameContainer.classList.remove('visible');
                    firmNameInput.required = false;
                    firmNameInput.value = '';
                }
            } else {
                firmTypeContainer.classList.add('hidden');
                firmTypeContainer.classList.remove('visible');
                firmTypeSelect.required = false;
                firmTypeSelect.value = 'individual';
                conditionalRow.classList.remove('two-columns');

                firmNameContainer.classList.add('hidden');
                firmNameContainer.classList.remove('visible');
                firmNameInput.required = false;
                firmNameInput.value = '';
            }
        }

        userTypeSelect.addEventListener('change', updateFieldVisibility);
        firmTypeSelect.addEventListener('change', updateFieldVisibility);
        updateFieldVisibility();
    }

    // Form submission
    const form = document.getElementById('registration-form');
    if (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            clearAllErrorMessages();

            const isPasswordValid = validatePassword(passwordInput.value);
            const isPasswordMatch = validatePasswordMatch();
            const isEmailValid = validateEmail(emailInput.value);
            const isContactValid = validateContactNumber(contactInput.value);
            const isTermsChecked = document.getElementById('terms').checked;

            if (!isPasswordValid || !isPasswordMatch || !isEmailValid || !isContactValid || !isTermsChecked) {
                if (!isEmailValid && emailError) emailError.style.display = 'block';
                if (!isContactValid && contactError) contactError.style.display = 'block';
                if (!isPasswordMatch && confirmPasswordError) confirmPasswordError.style.display = 'block';

                if (!isEmailValid) emailInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
                else if (!isContactValid) contactInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
                else if (!isPasswordValid) passwordInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
                else if (!isPasswordMatch) confirmPasswordInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
                return;
            }

            const registerBtn = document.getElementById('register-btn');
            if (registerBtn) {
                registerBtn.classList.add('loading');
                registerBtn.disabled = true;
            }

            const formData = new FormData(this);
            fetch(this.action, {
                method: 'POST',
                body: formData,
                credentials: 'same-origin'
            })
                .then(response => response.json().catch(() => ({
                    success: false,
                    message: 'Server error occurred. Please try again.',
                    errors: {}
                })))
                .then(data => {
                    if (registerBtn) {
                        registerBtn.classList.remove('loading');
                        registerBtn.disabled = false;
                    }
                    if (data.success) {
                        showNotification('success-notification');
                        resetForm();
                        if (data.redirect_url) {
                            setTimeout(() => {
                                window.location.href = data.redirect_url;
                            }, 3000);
                        }
                    } else {
                        if (data.errors) {
                            handleFormErrors(data.errors);
                        } else {
                            showNotification('error-notification', data.message || 'Registration failed. Please try again.');
                        }
                    }
                })
                .catch(error => {
                    console.error('Registration error:', error);
                    if (registerBtn) {
                        registerBtn.classList.remove('loading');
                        registerBtn.disabled = false;
                    }
                    showNotification('error-notification', 'An error occurred while processing your registration. Please try again.');
                });
        });
    }

    function resetForm() {
        const form = document.getElementById('registration-form');
        if (!form) return;

        form.reset();
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.classList.remove('valid-email', 'invalid-email', 'valid-password', 'invalid-password', 'valid-contact', 'invalid-contact');
            input.style.borderColor = '';
        });

        if (passwordStrengthMeter) {
            passwordStrengthMeter.style.width = '0%';
            passwordStrengthMeter.className = '';
        }

        if (passwordStrengthText) passwordStrengthText.textContent = '';

        const requirements = document.querySelectorAll('.requirement');
        requirements.forEach(req => {
            const icon = req.querySelector('i');
            if (icon) {
                icon.classList.remove('fa-check-circle', 'valid');
                icon.classList.add('fa-circle', 'invalid');
            }
            req.classList.remove('valid');
            req.classList.add('invalid');
        });

        clearAllErrorMessages();

        const userTypeSelect = document.getElementById('user_type');
        if (userTypeSelect) {
            const event = new Event('change');
            userTypeSelect.dispatchEvent(event);
        }
    }

    function clearAllErrorMessages() {
        const errorMessages = document.querySelectorAll('.error-message');
        errorMessages.forEach(error => {
            error.style.display = 'none';
        });
    }

    function handleFormErrors(errors) {
        for (const fieldName in errors) {
            const field = document.getElementById(fieldName);
            if (field) {
                field.classList.add('invalid-' + fieldName);
                field.classList.remove('valid-' + fieldName);
                let errorContainer = document.getElementById(fieldName + '_error');
                if (!errorContainer) {
                    errorContainer = document.createElement('div');
                    errorContainer.id = fieldName + '_error';
                    errorContainer.className = 'error-message';
                    field.parentElement.after(errorContainer);
                }
                errorContainer.textContent = errors[fieldName][0];
                errorContainer.style.display = 'block';
                field.scrollIntoView({ behavior: 'smooth', block: 'center' });
            } else if (fieldName === 'non_field_errors' || fieldName === '__all__') {
                showNotification('error-notification', errors[fieldName][0]);
            }
        }
    }

    const style = document.createElement('style');
    style.textContent = `
        .valid-email, .valid-password, .valid-contact {
            border-color: #28a745 !important;
        }
        .invalid-email, .invalid-password, .invalid-contact {
            border-color: #dc3545 !important;
        }
    `;
    document.head.appendChild(style);

    initializeConditionalFields();
});
function validateForm() {
    const fields = ['first_name', 'last_name', 'email', 'contact_number', 'user_type', 'password']; // Update 'phone' to 'contact_number'
    let isValid = true;

    fields.forEach(fieldName => {
        const field = document.getElementById(fieldName);
        if (!validateField(field)) {
            console.log(`Validation failed for: ${fieldName}`); // Debug log
            isValid = false;
        }
    });

    // Check password match
    if (!validatePasswordMatch()) {
        console.log("Password match validation failed");
        isValid = false;
    }

    // Check terms agreement
    const terms = document.getElementById('terms');
    if (!terms.checked) {
        console.log("Terms not checked");
        showNotification('error-notification', 'Please accept the Terms of Service and Privacy Policy');
        isValid = false;
    }

    return isValid;
}
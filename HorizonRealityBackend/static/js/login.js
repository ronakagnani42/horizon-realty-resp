// Toggle password visibility
function togglePassword(id) {
    const passwordInput = document.getElementById(id);
    const icon = document.querySelector('.toggle-password i');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// Password Reset Modal Functions
function openResetModal() {
    document.getElementById('passwordResetModal').style.display = 'block';
    document.getElementById('reset-email').focus();
}

function closeResetModal() {
    document.getElementById('passwordResetModal').style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('passwordResetModal');
    if (event.target === modal) {
        closeResetModal();
    }
};

// Optional: Add basic client-side validation if desired
document.getElementById('passwordResetForm').addEventListener('submit', function(e) {
    const email = document.getElementById('reset-email').value;
    
    // Basic email validation if needed
    if (!email || !email.includes('@')) {
        e.preventDefault();
        alert('Please enter a valid email address');
        return;
    }
    
    // No need to prevent default or use fetch API
    // Django will handle the form submission and redirect to the password_reset_done URL
});

// Optional: If you want to add custom validation to the main login form
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('form[action*="login"]');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const emailInput = document.getElementById('email');
            const passwordInput = document.getElementById('password');
            const termsCheckbox = document.getElementById('terms');
            
            // Basic validation
            if (!emailInput.value || !passwordInput.value) {
                e.preventDefault();
                alert('Please enter both email and password');
                return;
            }
            
            if (!termsCheckbox.checked) {
                e.preventDefault();
                alert('Please agree to the Terms of Service');
                return;
            }
            
            // Form is valid, let it submit naturally
        });
    }
});

// Escape key closes modal
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeResetModal();
    }
});
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing favorites functionality...');
    
    // Enhanced Toast Notification System
    function showToast(message, type = 'info') {
        console.log('Showing toast:', message, type);
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            console.error('Toast container not found!');
            return;
        }
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const iconMap = {
            success: 'bi-check-circle-fill',
            error: 'bi-x-circle-fill',
            info: 'bi-info-circle-fill'
        };
        
        toast.innerHTML = `
            <div class="toast-content">
                <i class="bi ${iconMap[type] || iconMap.info}"></i>
                <span>${message}</span>
            </div>
            <span class="toast-close">&times;</span>
        `;
        
        toastContainer.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Auto remove after 4 seconds
        const autoRemove = setTimeout(() => removeToast(toast), 4000);
        
        // Manual close
        toast.querySelector('.toast-close').addEventListener('click', () => {
            clearTimeout(autoRemove);
            removeToast(toast);
        });
    }
    
    function removeToast(toast) {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }

    // Utility function to get CSRF token
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
    
    // DEBUG: Check if favorite buttons exist
    const favoriteButtons = document.querySelectorAll('.favorite-btn');
    console.log('Found favorite buttons:', favoriteButtons.length);
    
    if (favoriteButtons.length === 0) {
        console.warn('No favorite buttons found! Check your HTML structure.');
        return;
    }
    
    // Enhanced Favorite Handling with Animations and DEBUG
    favoriteButtons.forEach((button, index) => {
        console.log(`Setting up favorite button ${index}:`, button);
        console.log(`Button property ID: ${button.dataset.propertyId}`);
        
        // Add visual feedback for debugging
        button.style.cursor = 'pointer';
        button.addEventListener('mouseenter', function() {
            console.log('Mouse entered favorite button');
            this.style.opacity = '0.8';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.opacity = '1';
        });
        
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            console.log('Favorite button clicked!');
            console.log('Event target:', e.target);
            console.log('Current target:', e.currentTarget);
            
            const propertyId = this.dataset.propertyId;
            console.log('Property ID:', propertyId);
            
            if (!propertyId) {
                console.error('Property ID not found in button data!');
                showToast('Error: Property ID not found', 'error');
                return;
            }
            
            const heartIcon = this.querySelector('i');
            console.log('Heart icon found:', heartIcon);
            
            // Add loading state
            this.style.pointerEvents = 'none';
            if (heartIcon) {
                heartIcon.style.opacity = '0.6';
            }
            
            // Show immediate feedback
            showToast('Processing...', 'info');
            
            console.log('Making AJAX request to:', `/favorite/${propertyId}/`);
            
            // Send AJAX request to toggle favorite
            fetch(`/favorite/${propertyId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            })
            .then(response => {
                console.log('Response status:', response.status);
                console.log('Response ok:', response.ok);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                return response.json();
            })
            .then(data => {
                console.log('Response data:', data);
                
                if (data.success) {
                    // Check if we're on the favorites page
                    const isOnFavoritesPage = window.location.pathname.includes('my-favorites') || 
                                            window.location.pathname.includes('favorites');
                    
                    console.log('Is on favorites page:', isOnFavoritesPage);
                    
                    if (isOnFavoritesPage) {
                        // Find the parent property card element
                        const propertyCard = button.closest('.col-md-6') || 
                                           button.closest('.col-lg-4') || 
                                           button.closest('.property-card').closest('div');
                        
                        console.log('Property card to remove:', propertyCard);
                        
                        if (propertyCard) {
                            // Add exit animation
                            propertyCard.style.transform = 'scale(0.8)';
                            propertyCard.style.opacity = '0';
                            propertyCard.style.transition = 'all 0.4s ease';
                            
                            setTimeout(() => {
                                propertyCard.remove();
                                
                                // Update the count with animation
                                const countElement = document.querySelector('.properties-found .count');
                                console.log('Count element:', countElement);
                                
                                if (countElement) {
                                    const currentCount = parseInt(countElement.textContent);
                                    console.log('Current count:', currentCount);
                                    
                                    countElement.style.transform = 'scale(1.2)';
                                    countElement.style.transition = 'transform 0.2s ease';
                                    
                                    setTimeout(() => {
                                        countElement.textContent = currentCount - 1;
                                        countElement.style.transform = 'scale(1)';
                                        
                                        // Check if no favorites left
                                        if (currentCount - 1 === 0) {
                                            console.log('No favorites left, showing empty state');
                                            // Show no results message
                                            setTimeout(() => {
                                                const containerElement = document.querySelector('.properties-section .container');
                                                if (containerElement) {
                                                    containerElement.innerHTML = `
                                                        <div class="section-header">
                                                            <h2>My Favorite Properties</h2>
                                                            <p>Properties you've saved as favorites</p>
                                                        </div>
                                                        <div class="no-results">
                                                            <i class="bi bi-heart"></i>
                                                            <h3>No Favorite Properties Yet</h3>
                                                            <p>You haven't added any properties to your favorites list. Browse our properties and click the heart icon to add them here.</p>
                                                            <a href="/properties/" class="btn-reset-filters">
                                                                <i class="bi bi-search"></i> Browse Properties
                                                            </a>
                                                        </div>
                                                    `;
                                                }
                                            }, 500);
                                        }
                                    }, 100);
                                }
                            }, 400);
                            
                            showToast(data.message || 'Property removed from favorites', 'success');
                        } else {
                            console.error('Could not find property card to remove');
                            showToast('Error: Could not remove property from page', 'error');
                        }
                    } else {
                        // If not on favorites page, just update the heart icon
                        if (data.is_favorite) {
                            this.classList.add('active');
                            if (heartIcon) {
                                heartIcon.classList.remove('bi-heart');
                                heartIcon.classList.add('bi-heart-fill');
                            }
                            showToast('Added to favorites', 'success');
                        } else {
                            this.classList.remove('active');
                            if (heartIcon) {
                                heartIcon.classList.remove('bi-heart-fill');
                                heartIcon.classList.add('bi-heart');
                            }
                            showToast('Removed from favorites', 'success');
                        }
                        
                        // Restore button state
                        this.style.pointerEvents = 'auto';
                        if (heartIcon) {
                            heartIcon.style.opacity = '1';
                        }
                    }
                } else {
                    console.error('Server returned success: false', data);
                    showToast(data.error || 'Failed to update favorites', 'error');
                    // Restore button state
                    this.style.pointerEvents = 'auto';
                    if (heartIcon) {
                        heartIcon.style.opacity = '1';
                    }
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
                showToast('Network error: ' + error.message, 'error');
                // Restore button state
                this.style.pointerEvents = 'auto';
                if (heartIcon) {
                    heartIcon.style.opacity = '1';
                }
            });
        });
    });
    
    // Additional debugging: Check if CSRF token exists
    const csrfToken = getCookie('csrftoken');
    console.log('CSRF token found:', !!csrfToken);
    if (!csrfToken) {
        console.warn('CSRF token not found! This might cause issues with POST requests.');
    }
    
    // Test click handler
    console.log('Favorites functionality initialized successfully!');
});

document.addEventListener('DOMContentLoaded', function() {
    const animatedBg = document.getElementById('animatedBg');
    
    if (!animatedBg) {
        console.log('Animated background element not found, skipping animation setup');
        return;
    }
    
    const heroSection = document.querySelector('.hero-section');
    
    // Function to create floating elements
    function createFloatingElement(type, className, icon) {
        const element = document.createElement('i');
        element.className = `bi ${icon} floating-element ${className}`;
        
        // Random positioning
        element.style.left = Math.random() * 100 + '%';
        element.style.top = Math.random() * 100 + '%';
        
        // Random animation delay
        element.style.animationDelay = Math.random() * 10 + 's';
        
        return element;
    }
    
    // Function to populate background with floating elements
    function populateBackground() {
        const elements = [
            // Hearts (most prominent)
            { type: 'heart', class: 'floating-heart', icon: 'bi-heart', count: 12 },
            { type: 'heart', class: 'floating-heart small', icon: 'bi-heart-fill', count: 8 },
            { type: 'heart', class: 'floating-heart large', icon: 'bi-heart', count: 6 },
            
            // House icons
            { type: 'house', class: 'floating-house', icon: 'bi-house-heart', count: 8 },
            { type: 'house', class: 'floating-house', icon: 'bi-house-door', count: 6 },
            
            // Stars
            { type: 'star', class: 'floating-star', icon: 'bi-star', count: 10 },
            { type: 'star', class: 'floating-star', icon: 'bi-star-fill', count: 8 },
            
            // Keys
            { type: 'key', class: 'floating-key', icon: 'bi-key', count: 5 },
            { type: 'key', class: 'floating-key', icon: 'bi-key-fill', count: 4 }
        ];
        
        elements.forEach(elementType => {
            for (let i = 0; i < elementType.count; i++) {
                const element = createFloatingElement(
                    elementType.type,
                    elementType.class,
                    elementType.icon
                );
                animatedBg.appendChild(element);
            }
        });
    }
    
    // Function to create heart pop effect
    function createHeartPop(x, y) {
        const heartPop = document.createElement('i');
        heartPop.className = 'bi bi-heart-fill heart-pop';
        heartPop.style.left = x + 'px';
        heartPop.style.top = y + 'px';
        
        animatedBg.appendChild(heartPop);
        
        // Remove after animation
        setTimeout(() => {
            if (heartPop.parentNode) {
                heartPop.parentNode.removeChild(heartPop);
            }
        }, 2000);
    }
    
    // Add click handler for heart pop effects
    if (heroSection) {
        heroSection.addEventListener('click', function(e) {
            const rect = heroSection.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            // Create multiple heart pops
            for (let i = 0; i < 3; i++) {
                setTimeout(() => {
                    createHeartPop(
                        x + (Math.random() - 0.5) * 100,
                        y + (Math.random() - 0.5) * 100
                    );
                }, i * 200);
            }
        });
    }
    
    // Initialize background
    populateBackground();
    
    // Add occasional random heart pops
    function randomHeartPop() {
        if (Math.random() > 0.7 && heroSection) { // 30% chance
            const rect = heroSection.getBoundingClientRect();
            createHeartPop(
                Math.random() * rect.width,
                Math.random() * rect.height
            );
        }
        
        // Schedule next random pop
        setTimeout(randomHeartPop, Math.random() * 5000 + 3000); // 3-8 seconds
    }
    
    // Start random heart pops
    setTimeout(randomHeartPop, 2000);
    
    // Refresh floating elements periodically to prevent performance issues
    setInterval(() => {
        // Remove old elements
        const oldElements = animatedBg.querySelectorAll('.floating-element');
        oldElements.forEach(el => {
            if (Math.random() > 0.8) { // Remove 20% randomly
                el.remove();
            }
        });
        
        // Add new ones if needed
        const currentCount = animatedBg.querySelectorAll('.floating-element').length;
        if (currentCount < 50) {
            const newElement = createFloatingElement(
                'heart',
                'floating-heart',
                Math.random() > 0.5 ? 'bi-heart' : 'bi-heart-fill'
            );
            animatedBg.appendChild(newElement);
        }
    }, 10000); // Every 10 seconds
    
    console.log('Animated background initialized with floating elements!');
});
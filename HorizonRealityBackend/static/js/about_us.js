document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded and parsed");
    
    // Fade-in animation setup
    const fadeElements = document.querySelectorAll('.fade-in');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, { threshold: 0.1 });
    
    fadeElements.forEach(element => observer.observe(element));
    
    // Read More / Read Less functionality for welcome text
    const welcomeContainer = document.querySelector('.welcome-text-container');
    const welcomePreview = document.querySelector('.welcome-text-preview');
    const welcomeFull = document.querySelector('.welcome-text-full');
    const welcomeButton = document.querySelector('.welcome-text-btn');
    
    if (welcomeButton && welcomePreview && welcomeFull) {
        welcomeButton.addEventListener('click', function(e) {
            e.preventDefault();
            console.log("Welcome text button clicked");
            
            if (welcomeFull.style.display === 'none' || getComputedStyle(welcomeFull).display === 'none') {
                console.log("Expanding full welcome text");
                welcomePreview.style.display = 'none';
                welcomeFull.style.display = 'block';
                welcomeButton.textContent = 'Read Less';
            } else {
                console.log("Collapsing full welcome text");
                welcomePreview.style.display = 'block';
                welcomeFull.style.display = 'none';
                welcomeButton.textContent = 'Read More';
            }
        });
    }
    
    // Read More / Read Less functionality with auto-closing others
    const teamCards = document.querySelectorAll('.team-member-profile-card');
    console.log("Found", teamCards.length, "team cards");
    
    teamCards.forEach(function(card, index) {
        console.log(`Setting up card #${index}`);
        
        const button = card.querySelector('.read-more-btn');
        const bioPreview = card.querySelector('.bio-preview');
        const bioFull = card.querySelector('.bio-full');
        
        if (!button || !bioPreview || !bioFull) {
            console.error(`Missing elements in card #${index}`);
            return;
        }
        
        button.addEventListener('click', function(e) {
            e.preventDefault();
            console.log(`Button clicked on card #${index}`);
            
            // Close all other cards first
            teamCards.forEach(function(otherCard, otherIndex) {
                if (otherCard !== card) {
                    const otherBioPreview = otherCard.querySelector('.bio-preview');
                    const otherBioFull = otherCard.querySelector('.bio-full');
                    const otherButton = otherCard.querySelector('.read-more-btn');
                    
                    if (otherBioPreview && otherBioFull && otherButton) {
                        otherBioPreview.style.display = 'block';
                        otherBioFull.style.display = 'none';
                        otherButton.textContent = 'Read More';
                        console.log(`Collapsed card #${otherIndex}`);
                    }
                }
            });
            
            // Toggle the clicked card
            if (bioFull.style.display === 'none' || getComputedStyle(bioFull).display === 'none') {
                console.log(`Expanding full bio in card #${index}`);
                bioPreview.style.display = 'none';
                bioFull.style.display = 'block';
                button.textContent = 'Read Less';
            } else {
                console.log(`Collapsing full bio in card #${index}`);
                bioPreview.style.display = 'block';
                bioFull.style.display = 'none';
                button.textContent = 'Read More';
            }
        });
    });
    
    // Header scroll effect
    const header = document.getElementById('header');
    if (header) {
        function toggleHeaderScrolled() {
            header.classList.toggle('scrolled', window.scrollY > 0);
        }
        toggleHeaderScrolled();
        window.addEventListener('scroll', toggleHeaderScrolled);
    }
});

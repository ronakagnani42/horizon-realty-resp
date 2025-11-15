document.addEventListener('DOMContentLoaded', function() {
    // Function to get CSRF cookie
    function getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
  
    // Handle inquiry form submission via AJAX
    const inquiryForm = document.getElementById('inquiryForm');
    const inquirySuccess = document.getElementById('inquiry-success');
    const brochureContainer = document.querySelector('.brochure-container');
  
    if (inquiryForm) {
      inquiryForm.addEventListener('submit', function(e) {
        e.preventDefault();
  
        // Show a simple loading state
        const submitBtn = this.querySelector('.submit-btn');
        submitBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Sending...';
        submitBtn.disabled = true;
  
        // Prepare form data
        const formData = new FormData(this);
  
        // Send AJAX request
        fetch(this.action, {
          method: 'POST',
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')  // Include CSRF token
          }
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            // Hide the form and show success message
            inquiryForm.style.display = 'none';
            inquirySuccess.style.display = 'block';
  
            // Show brochure download button in sidebar if available
            if (brochureContainer) {
              brochureContainer.style.display = 'block';
            }
          } else {
            // Handle form errors
            alert('There was an error with your submission. Please try again.');
            submitBtn.innerHTML = 'Send Inquiry';
            submitBtn.disabled = false;
          }
        })
        .catch(error => {
          console.error('Error:', error);
          alert('An unexpected error occurred. Please try again later.');
          submitBtn.innerHTML = 'Send Inquiry';
          submitBtn.disabled = false;
        });
      });
    }
  
    // Gallery Thumbnails Navigation
    const galleryThumbnails = document.querySelectorAll('.gallery-thumbnail');
    galleryThumbnails.forEach(thumbnail => {
      thumbnail.addEventListener('click', function() {
        // Remove active class from all thumbnails
        galleryThumbnails.forEach(item => item.classList.remove('active'));
        // Add active class to clicked thumbnail
        this.classList.add('active');
      });
    });
  
    // Handle carousel slide event to update active thumbnail
    const galleryCarousel = document.getElementById('propertyGalleryCarousel');
    if (galleryCarousel) {
      galleryCarousel.addEventListener('slide.bs.carousel', function(e) {
        // Remove active class from all thumbnails
        galleryThumbnails.forEach(item => item.classList.remove('active'));
        // Add active class to corresponding thumbnail
        galleryThumbnails[e.to].classList.add('active');
  
        // Pause all videos when sliding
        const videos = document.querySelectorAll('.property-gallery-video');
        videos.forEach(video => {
          video.pause();
        });
      });
    }
  
    // Fullscreen Gallery
    const carouselItems = document.querySelectorAll('.carousel-item');
    const fullscreenGallery = document.getElementById('fullscreenGallery');
    const fullscreenContent = document.getElementById('fullscreenContent');
    const fullscreenClose = document.getElementById('fullscreenClose');
    const fullscreenPrev = document.getElementById('fullscreenPrev');
    const fullscreenNext = document.getElementById('fullscreenNext');
  
    let currentFullscreenIndex = 0;
    const mediaItems = [];
  
    // Collect all media items and their types
    carouselItems.forEach((item, index) => {
      const mediaType = item.getAttribute('data-media-type');
      const mediaUrl = item.getAttribute('data-media-url');
  
      if (mediaType && mediaUrl) {
        mediaItems.push({
          type: mediaType,
          url: mediaUrl,
          caption: item.querySelector('.carousel-caption p')?.textContent || ''
        });
  
        // Add click event to open fullscreen
        item.addEventListener('click', function() {
          openFullscreen(index);
        });
      }
    });
  
    // Open fullscreen gallery
    function openFullscreen(index) {
      if (mediaItems.length === 0) return;
  
      currentFullscreenIndex = index;
      updateFullscreenContent();
      fullscreenGallery.classList.add('active');
      document.body.style.overflow = 'hidden'; // Prevent body scrolling
    }
  
    // Close fullscreen gallery
    fullscreenClose.addEventListener('click', function() {
      fullscreenGallery.classList.remove('active');
      document.body.style.overflow = ''; // Restore body scrolling
  
      // Pause video if playing
      const video = fullscreenContent.querySelector('video');
      if (video) {
        video.pause();
      }
    });
  
    // Navigate to previous item
    fullscreenPrev.addEventListener('click', function() {
      navigateFullscreen(-1);
    });
  
    // Navigate to next item
    fullscreenNext.addEventListener('click', function() {
      navigateFullscreen(1);
    });
  
    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
      if (!fullscreenGallery.classList.contains('active')) return;
  
      if (e.key === 'Escape') {
        fullscreenClose.click();
      } else if (e.key === 'ArrowLeft') {
        navigateFullscreen(-1);
      } else if (e.key === 'ArrowRight') {
        navigateFullscreen(1);
      }
    });
  
    // Navigate to previous/next item
    function navigateFullscreen(direction) {
      // Pause current video if playing
      const video = fullscreenContent.querySelector('video');
      if (video) {
        video.pause();
      }
  
      // Update index
      currentFullscreenIndex += direction;
  
      // Wrap around
      if (currentFullscreenIndex < 0) {
        currentFullscreenIndex = mediaItems.length - 1;
      } else if (currentFullscreenIndex >= mediaItems.length) {
        currentFullscreenIndex = 0;
      }
  
      updateFullscreenContent();
    }
  
    // Update fullscreen content
    function updateFullscreenContent() {
      const item = mediaItems[currentFullscreenIndex];
  
      fullscreenContent.innerHTML = '';
  
      if (item.type === 'image') {
        const img = document.createElement('img');
        img.className = 'fullscreen-image';
        img.src = item.url;
        img.alt = item.caption || 'Property Image';
        fullscreenContent.appendChild(img);
  
        if (item.caption) {
          const caption = document.createElement('div');
          caption.className = 'mt-3 text-center text-light';
          caption.textContent = item.caption;
          fullscreenContent.appendChild(caption);
        }
      } else if (item.type === 'video') {
        // Add loading indicator
        const loading = document.createElement('div');
        loading.className = 'video-loading';
        loading.innerHTML = '<i class="bi bi-arrow-repeat spin"></i>';
        fullscreenContent.appendChild(loading);
  
        const video = document.createElement('video');
        video.className = 'fullscreen-video';
        video.controls = true;
        video.src = item.url;
        video.addEventListener('loadeddata', function() {
          // Remove loading indicator once video is loaded
          fullscreenContent.querySelector('.video-loading')?.remove();
        });
        fullscreenContent.appendChild(video);
  
        if (item.caption) {
          const caption = document.createElement('div');
          caption.className = 'mt-3 text-center text-light';
          caption.textContent = item.caption;
          fullscreenContent.appendChild(caption);
        }
      }
    }
  });

document.addEventListener('DOMContentLoaded', function() {
  // Check if we have more than 3 properties
  const propertySlides = document.querySelectorAll('.related-properties-swiper .swiper-slide');
  const hasMoreThanThree = propertySlides.length > 3;
  
  // Initialize Swiper
  const relatedPropertiesSwiper = new Swiper('.related-properties-swiper', {
    slidesPerView: 3, // Changed from 1 to 3 for desktop default
    spaceBetween: 30,
    loop: hasMoreThanThree,
    autoplay: hasMoreThanThree ? {
      delay: 5000,
      disableOnInteraction: false,
    } : false,
    
    // Navigation
    navigation: hasMoreThanThree ? {
      nextEl: '.related-swiper-next',
      prevEl: '.related-swiper-prev',
    } : false,
    
    // Pagination
    pagination: hasMoreThanThree ? {
      el: '.related-swiper-pagination',
      clickable: true,
    } : false,
    
    // Responsive breakpoints
    breakpoints: {
      320: { // Added small mobile breakpoint
        slidesPerView: 1,
        spaceBetween: 15,
      },
      576: {
        slidesPerView: 1,
        spaceBetween: 20,
      },
      768: {
        slidesPerView: 2,
        spaceBetween: 25,
      },
      992: {
        slidesPerView: 3,
        spaceBetween: 25,
      },
      1200: {
        slidesPerView: 3,
        spaceBetween: 30,
      }
    },
    
    // Effects
    effect: 'slide',
    speed: 800,
    
    // Touch settings
    touchRatio: 1,
    touchAngle: 45,
    simulateTouch: true,
    
    // Prevent clicks during transition
    preventClicks: true,
    preventClicksPropagation: true,
    
    // Accessibility
    a11y: {
      enabled: true,
      prevSlideMessage: 'Previous property',
      nextSlideMessage: 'Next property',
    }
  });
  
  // Add hover pause for autoplay
  if (hasMoreThanThree) {
    const swiperContainer = document.querySelector('.related-properties-swiper');
    swiperContainer.addEventListener('mouseenter', () => {
      relatedPropertiesSwiper.autoplay.stop();
    });
    
    swiperContainer.addEventListener('mouseleave', () => {
      relatedPropertiesSwiper.autoplay.start();
    });
  }
});
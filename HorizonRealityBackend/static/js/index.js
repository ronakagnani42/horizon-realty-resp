document.addEventListener('DOMContentLoaded', function() {
  // Initialize AOS with custom settings
  AOS.init({
    duration: 1000,
    easing: 'ease-in-out',
    once: true,
    mirror: false
  });

  // Services Swiper initialization
  const servicesSwiper = new Swiper(".mySwiper", {
    slidesPerView: 1,
    spaceBetween: 20,
    loop: true,
    speed: 800,
    loopFillGroupWithBlank: true,
    centeredSlides: false,
    autoplay: {
      delay: 3000,
      disableOnInteraction: false
    },
    breakpoints: {
      1400: { 
        slidesPerView: 4,
        spaceBetween: 30
      },
      1200: { 
        slidesPerView: 3, 
        spaceBetween: 30
      },
      992: { 
        slidesPerView: 2, 
        spaceBetween: 25
      },
      768: { 
        slidesPerView: 2, 
        spaceBetween: 20
      },
      576: { 
        slidesPerView: 1, 
        spaceBetween: 15
      }
    },
    effect: "slide",
    pagination: {
      el: ".swiper-pagination",
      clickable: true
    },
    watchOverflow: true,
    roundLengths: true,
    normalizeSlideIndex: true,
    slidesOffsetBefore: 0,
    slidesOffsetAfter: 0
  });

  // Testimonials Swiper initialization
  const testimonialsSwiper = new Swiper('.testimonialsSwiper', {
    slidesPerView: 1,
    spaceBetween: 30,
    initialSlide: 0,
    loop: true,
    speed: 800,
    loopFillGroupWithBlank: true,
    centeredSlides: false,
    autoplay: {
      delay: 4000,
      disableOnInteraction: false,
      waitForTransition: true,
      pauseOnMouseEnter: true
    },
    effect: "slide",
    pagination: {
      el: '.swiper-pagination',
      clickable: true
    },
    breakpoints: {
      1400: {
        slidesPerView: 3,
        spaceBetween: 30
      },
      1200: {
        slidesPerView: 3,
        spaceBetween: 30
      },
      992: {
        slidesPerView: 2,
        spaceBetween: 20
      },
      768: {
        slidesPerView: 2,
        spaceBetween: 20
      },
      576: {
        slidesPerView: 1,
        spaceBetween: 15
      }
    },
    watchOverflow: true,
    roundLengths: true,
    normalizeSlideIndex: true,
    slidesOffsetBefore: 0,
    slidesOffsetAfter: 0
  });
  
  // Force start the autoplay immediately
  testimonialsSwiper.autoplay.start();
  
  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      
      const targetId = this.getAttribute('href');
      if(targetId === '#') return;
      
      const targetElement = document.querySelector(targetId);
      if(targetElement) {
        window.scrollTo({
          top: targetElement.offsetTop - 80,
          behavior: 'smooth'
        });
      }
    });
  });
  
  // Portfolio isotope and filter - IMPROVED VERSION
  let portfolioIsotope = document.querySelector('.isotope-container');
  if (portfolioIsotope) {
    let portfolioFilters = document.querySelectorAll('.portfolio-filters li');
    
    window.addEventListener('load', () => {
      // Wait for all images to load before initializing Isotope
      if (typeof imagesLoaded !== 'undefined') {
        imagesLoaded(portfolioIsotope, function() {
          initIsotope();
        });
      } else {
        // Fallback if imagesLoaded is not available
        setTimeout(initIsotope, 500);
      }
      
      function initIsotope() {
        let iso = new Isotope(portfolioIsotope, {
          itemSelector: '.isotope-item',
          layoutMode: 'fitRows',
          fitRows: {
            gutter: 30
          }
        });
        
        // Initial filter
        iso.arrange({
          filter: '*'
        });
        
        // Filter items on button click
        portfolioFilters.forEach(filter => {
          filter.addEventListener('click', function(e) {
            e.preventDefault();
            
            portfolioFilters.forEach(el => {
              el.classList.remove('filter-active');
            });
            this.classList.add('filter-active');
            
            iso.arrange({
              filter: this.getAttribute('data-filter')
            });
            
            // Re-layout Isotope after filtering
            setTimeout(function() {
              iso.layout();
            }, 300);
          });
        });
      }
    });
  }
  
  // Initialize GLightbox for portfolio items
  const glightbox = GLightbox({
    selector: '.glightbox',
    touchNavigation: true,
    loop: true,
    autoplayVideos: true
  });
  
  // PureCounter initialization
  new PureCounter();
});
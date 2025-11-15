  // Open filter tabs
  function openFilterTab(tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("filter-content");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].classList.remove("active");
    }
    tablinks = document.getElementsByClassName("filter-tab");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].classList.remove("active");
    }
    document.getElementById(tabName).classList.add("active");
    event.currentTarget.classList.add("active");
  }
  
  // Open property type tabs
  function openPropertyType(formName, element) {
    var i, formcontent, formlinks;
    formcontent = document.getElementsByClassName("filter-form");
    for (i = 0; i < formcontent.length; i++) {
      formcontent[i].classList.remove("active");
    }
    formlinks = document.getElementsByClassName("property-type-tab");
    for (i = 0; i < formlinks.length; i++) {
      formlinks[i].classList.remove("active");
    }
    document.getElementById(formName + "-form").classList.add("active");
    element.classList.add("active");
  }
  
  // Slider functionality for residential buy
  const areaResSlider = document.getElementById("area-res-slider");
  const areaResValue = document.getElementById("area-res-value");
  areaResSlider.oninput = function() {
    areaResValue.textContent = this.value + " sq ft";
  }
  
  const budgetResSlider = document.getElementById("budget-res-slider");
  const budgetResValue = document.getElementById("budget-res-value");
  budgetResSlider.oninput = function() {
    budgetResValue.textContent = "₹" + formatPrice(this.value);
  }
  
  // Slider functionality for commercial buy
  const areaComSlider = document.getElementById("area-com-slider");
  const areaComValue = document.getElementById("area-com-value");
  areaComSlider.oninput = function() {
    areaComValue.textContent = this.value + " sq ft";
  }
  
  const budgetComSlider = document.getElementById("budget-com-slider");
  const budgetComValue = document.getElementById("budget-com-value");
  budgetComSlider.oninput = function() {
    budgetComValue.textContent = "₹" + formatPrice(this.value);
  }
  
  // Format price with commas for Indian numbering system
  function formatPrice(price) {
    price = parseInt(price);
    if (price >= 10000000) {
      return (price / 10000000).toFixed(2) + " Cr";
    } else if (price >= 100000) {
      return (price / 100000).toFixed(2) + " Lakh";
    } else {
      return price.toLocaleString('en-IN');
    }
  }
    // Pass Django context to JavaScript
  const djangoActiveTab = '{{ active_tab|default:"" }}';
  
  function initializePage() {
    const urlParams = new URLSearchParams(window.location.search);
    const urlTab = urlParams.get('tab');
    
    // Priority: Django context > URL parameter > default
    let activeTab = 'buy'; // default
    
    if (djangoActiveTab) {
      // Django passed an active tab (usually after form submission with errors)
      activeTab = djangoActiveTab;
    } else if (urlTab) {
      // URL has tab parameter (usually after successful submission redirect)
      activeTab = urlTab;
    }
    
    openFilterTab(activeTab);
  }

  // Call initialization when page loads
  document.addEventListener('DOMContentLoaded', initializePage);

  // Open filter tabs
  function openFilterTab(tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("filter-content");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].classList.remove("active");
    }
    tablinks = document.getElementsByClassName("filter-tab");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].classList.remove("active");
    }
    document.getElementById(tabName).classList.add("active");
    document.getElementById(tabName + "-tab").classList.add("active");
  }
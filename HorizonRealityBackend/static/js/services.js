function openFilterTab(tabName) {
  // Hide all filter content
  var filterContents = document.getElementsByClassName("filter-content");
  for (var i = 0; i < filterContents.length; i++) {
    filterContents[i].classList.remove("active");
  }
  
  // Deactivate all tabs
  var filterTabs = document.getElementsByClassName("filter-tab");
  for (var i = 0; i < filterTabs.length; i++) {
    filterTabs[i].classList.remove("active");
  }
  
  // Show the selected tab content
  document.getElementById(tabName).classList.add("active");
  
  // Activate the clicked tab
  event.currentTarget.classList.add("active");
  
  // Reset property type tabs to first option
  if (tabName === "buy") {
    openPropertyType('residential', document.querySelector('#buy .property-type-tab'));
  } else if (tabName === "sell") {
    openPropertyType('residential-sell', document.querySelector('#sell .property-type-tab'));
  }
}

function openPropertyType(formId, tabElement) {
  // Hide all property type forms
  var parentTab = tabElement.parentElement.parentElement.id;
  var forms = document.querySelectorAll("#" + parentTab + " .filter-form");
  for (var i = 0; i < forms.length; i++) {
    forms[i].classList.remove("active");
  }
  
  // Deactivate all property type tabs
  var tabs = tabElement.parentElement.querySelectorAll(".property-type-tab");
  for (var i = 0; i < tabs.length; i++) {
    tabs[i].classList.remove("active");
  }
  
  // Show the selected form
  document.getElementById(formId + "-form").classList.add("active");
  
  // Activate the clicked tab
  tabElement.classList.add("active");
}

// Range slider for residential area
var resAreaSlider = document.getElementById("area-res-slider");
var resAreaValue = document.getElementById("area-res-value");

resAreaSlider.oninput = function() {
  resAreaValue.textContent = this.value + " sq ft";
}

// Range slider for residential budget
var resBudgetSlider = document.getElementById("budget-res-slider");
var resBudgetValue = document.getElementById("budget-res-value");

resBudgetSlider.oninput = function() {
  var value = this.value;
  if (value >= 10000000) {
    resBudgetValue.textContent = "₹" + (value / 10000000).toFixed(2) + " Cr";
  } else if (value >= 100000) {
    resBudgetValue.textContent = "₹" + (value / 100000).toFixed(2) + " Lac";
  } else {
    resBudgetValue.textContent = "₹" + value.toLocaleString();
  }
}

// Range slider for commercial area
var comAreaSlider = document.getElementById("area-com-slider");
var comAreaValue = document.getElementById("area-com-value");

comAreaSlider.oninput = function() {
  comAreaValue.textContent = this.value + " sq ft";
}

// Range slider for commercial budget
var comBudgetSlider = document.getElementById("budget-com-slider");
var comBudgetValue = document.getElementById("budget-com-value");

comBudgetSlider.oninput = function() {
  var value = this.value;
  if (value >= 10000000) {
    comBudgetValue.textContent = "₹" + (value / 10000000).toFixed(2) + " Cr";
  } else if (value >= 100000) {
    comBudgetValue.textContent = "₹" + (value / 100000).toFixed(2) + " Lac";
  } else {
    comBudgetValue.textContent = "₹" + value.toLocaleString();
  }
}

// Form submission handler for Interior Design Inquiry
document.addEventListener('DOMContentLoaded', function() {
  const interiorForm = document.getElementById('interior-form');
  if (interiorForm) {
    interiorForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // Hide the form
      const formElements = interiorForm.querySelector('.form-elements');
      const successMessage = interiorForm.querySelector('.success-message');
      
      formElements.style.display = 'none';
      successMessage.style.display = 'block';
      
      // Reset form after 5 seconds (optional)
      setTimeout(function() {
        interiorForm.reset();
        formElements.style.display = 'block';
        successMessage.style.display = 'none';
      }, 10000);
    });
  }
});
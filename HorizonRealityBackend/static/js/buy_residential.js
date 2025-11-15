 document.addEventListener('DOMContentLoaded', function() {
    // Activate the interior tab
    const interiorTab = document.getElementById('buy');
    if (interiorTab) {
        interiorTab.classList.add('active');
    }
    
    // Show the interior form content
    const interiorContent = document.getElementById('buy');
    if (interiorContent) {
        interiorContent.classList.add('active');
        interiorContent.style.display = 'block';
    }
});

// Your existing openFilterTab function (if you have one)
function openFilterTab(tabName) {
    // Hide all filter content
    const filterContents = document.getElementsByClassName('filter-content');
    for (let i = 0; i < filterContents.length; i++) {
        filterContents[i].classList.remove('active');
        filterContents[i].style.display = 'none';
    }
    
    // Remove active class from all tabs
    const filterTabs = document.getElementsByClassName('filter-tab');
    for (let i = 0; i < filterTabs.length; i++) {
        filterTabs[i].classList.remove('active');
    }
    
    // Show selected tab content
    const selectedContent = document.getElementById(tabName);
    if (selectedContent) {
        selectedContent.classList.add('active');
        selectedContent.style.display = 'block';
    }
    
    // Add active class to clicked tab
    const selectedTab = document.getElementById(tabName + '-tab');
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
}
document.addEventListener('DOMContentLoaded', function () {
  const header = document.getElementById('header');

  function toggleHeaderScrolled() {
    if (header) {
      header.classList.toggle('scrolled', window.scrollY > 0);
    }
  }
  toggleHeaderScrolled();
  window.addEventListener('scroll', toggleHeaderScrolled);

  // Check if paginationData exists
  if (typeof paginationData === 'undefined') {
    console.error('paginationData is not defined');
    return;
  }

  let currentPage = paginationData.currentPage;
  const loadMoreBtn = document.getElementById('load-more');
  const loadMoreContainer = document.getElementById('load-more-container');
  const loader = document.getElementById('loader');
  const container = document.getElementById('blog-container');
  
  // Debug logs
  console.log('Pagination Data:', paginationData);
  console.log('Current Page:', currentPage);
  console.log('Has Next:', paginationData.hasNext);
  console.log('Total Pages:', paginationData.totalPages);
  console.log('Load More Button:', loadMoreBtn);
  
  // Only hide if there's genuinely no next page
  if (!paginationData.hasNext) {
    console.log('No next page - hiding load more button');
    if (loadMoreContainer) {
      loadMoreContainer.style.display = 'none';
    }
  } else {
    console.log('Has next page - showing load more button');
    if (loadMoreContainer) {
      loadMoreContainer.style.display = 'block';
    }
  }

  if (loadMoreBtn) {
    loadMoreBtn.addEventListener('click', function () {
      console.log('Load More button clicked');
      currentPage += 1;
      console.log('Loading page:', currentPage);
      
      loader.style.display = 'inline-block';
      loadMoreBtn.disabled = true;
      loadMoreBtn.style.opacity = '0.5';

      fetch(`?page=${currentPage}`, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(response => {
        console.log('Response status:', response.status);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('Received data:', data);
        console.log('Number of blogs:', data.blogs.length);
        
        if (data.blogs.length > 0) {
          data.blogs.forEach(blog => {
            const blogDate = new Date(blog.created_at).toLocaleDateString('en-US', {
              month: 'long',
              day: 'numeric',
              year: 'numeric'
            });

            const blogCard = `
              <div class="blog-card">
                <a href="/blogs/${blog.slug}/">
                  <img src="${blog.image}" alt="${escapeHtml(blog.title)}">
                </a>
                <div class="blog-content">
                  <div class="blog-date">
                    <i class="bi bi-calendar-date"></i> ${blogDate}
                  </div>
                  <a href="/blogs/${blog.slug}/">
                    <h3>${escapeHtml(blog.title)}</h3>
                  </a>
                  <p>${blog.description ? escapeHtml(blog.description.slice(0, 100)) + '...' : 'No description available.'}</p>
                  <a href="/blogs/${blog.slug}/" class="read-more">
                    Read More <i class="bi bi-arrow-right"></i>
                  </a>
                </div>
              </div>
            `;
            container.insertAdjacentHTML('beforeend', blogCard);
          });
          
          console.log('Blogs added to container');
        }

        // Check if there are more pages
        if (!data.has_next || currentPage >= data.total_pages || data.blogs.length === 0) {
          console.log('No more pages - hiding load more button');
          loadMoreContainer.style.display = 'none';
        } else {
          console.log('More pages available - keeping button enabled');
          loadMoreBtn.disabled = false;
          loadMoreBtn.style.opacity = '1';
        }
      })
      .catch(error => {
        console.error('Error loading more blogs:', error);
        loadMoreBtn.disabled = false;
        loadMoreBtn.style.opacity = '1';
        alert('Failed to load more blogs. Please try again.');
      })
      .finally(() => {
        loader.style.display = 'none';
      });
    });
  } else {
    console.error('Load More button not found in DOM');
  }
  
  // Helper function to escape HTML
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
});
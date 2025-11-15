document.addEventListener('DOMContentLoaded', function () {
  const header = document.getElementById('header');

  function toggleHeaderScrolled() {
    header.classList.toggle('scrolled', window.scrollY > 0);
  }
  toggleHeaderScrolled();
  window.addEventListener('scroll', toggleHeaderScrolled);

  let currentPage = paginationData.currentPage;
  const loadMoreBtn = document.getElementById('load-more');
  const loadMoreContainer = document.getElementById('load-more-container');
  const loader = document.getElementById('loader');
  const container = document.getElementById('blog-container');
  
  if (!paginationData.hasNext) {
    loadMoreContainer.style.display = 'none';
  }

  if (loadMoreBtn) {
    loadMoreBtn.addEventListener('click', function () {
      currentPage += 1;
      loader.style.display = 'inline-block';
      loadMoreBtn.disabled = true;

      fetch(`?page=${currentPage}`, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(response => response.json())
      .then(data => {
        if (data.blogs.length > 0) {
          data.blogs.forEach(blog => {
            const blogDate = new Date(blog.created_at).toLocaleDateString('en-US', {
              month: 'long',
              day: 'numeric',
              year: 'numeric'
            });

            const blogCard = `
              <div class="blog-card">
                <a href="/blogs/${blog.pk}/">
                  <img src="${blog.image}" alt="${blog.title}">
                </a>
                <div class="blog-content">
                  <div class="blog-date">
                    <i class="bi bi-calendar-date"></i> ${blogDate}
                  </div>
                  <a href="/blogs/${blog.pk}/">
                    <h3>${blog.title}</h3>
                  </a>
                  <p>${blog.description ? blog.description.slice(0, 100) + '...' : 'No description available.'}</p>
                  <a href="/blogs/${blog.pk}/" class="read-more">
                    Read More <i class="bi bi-arrow-right"></i>
                  </a>
                </div>
              </div>
            `;
            container.insertAdjacentHTML('beforeend', blogCard);
          });
        } else if (currentPage === 1) {
          container.innerHTML = `
            <div class="no-blogs-message" style="text-align:center; padding:50px; font-size:20px;">
              No blogs available.
            </div>
          `;
        }

        if (!data.has_next || currentPage >= data.total_pages || data.blogs.length === 0) {
          loadMoreContainer.style.display = 'none';
        } else {
          loadMoreBtn.disabled = false;
        }
      })
      .catch(error => {
        console.error('Error loading more blogs:', error);
        loadMoreBtn.disabled = false;
      })
      .finally(() => {
        loader.style.display = 'none';
      });
    });
  }
});
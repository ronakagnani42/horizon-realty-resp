from django.shortcuts import render,get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Blog
# Create your views here.
def blogs_view(request):
    '''
    Displays paginated blog list with support for AJAX loading.
    '''
    blogs = Blog.objects.filter(is_visible=True).order_by('-created_at')
    paginator = Paginator(blogs, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        blogs_data = []
        for blog in page_obj:
            blogs_data.append({
                'title': blog.title,
                'image': blog.image.url,
                'description': blog.description,
                'slug': blog.slug,
                'created_at': blog.created_at.isoformat()
            })
        return JsonResponse({
            'blogs': blogs_data,
            'has_next': page_obj.has_next(),
            'total_pages': paginator.num_pages
        })
    
    return render(request, 'blogs/blogs.html', {'page_obj': page_obj, 'no_blogs': not blogs.exists()})


def blog_detail(request, slug):
    '''
    Displays the detailed view of a specific blog post.
    - Retrieves the blog by slug only if it's marked as visible.
    - If not found, returns a 404 error.
    '''
    blog = get_object_or_404(Blog, slug=slug, is_visible=True)
    return render(request, 'blogs/blog_details.html', {'blog': blog})
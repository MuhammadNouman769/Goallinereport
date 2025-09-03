
# Create your views here.
# apps/glrdesign/views.py  (ya agar app nahi, to project ke views.py me)

from django.shortcuts import render

def index(request):
    return render(request, 'glrdesign/index.html')
 

def author(request):
    return render(request, 'glrdesign/author.html')

def glr_blog_details(request):
    return render(request, 'glrdesign/blog-details.html')

def glr_column_layout(request):
    return render(request, 'glrdesign/column-layout-grid.html')

def glr_coming_soon(request):
    return render(request, 'glrdesign/coming-soon.html')

def glr_error(request):
    return render(request, 'glrdesign/error.html')

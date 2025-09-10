from django.shortcuts import render

def index(request):
    """Home page view for the glrdesign app"""
    context = {
        'page_title': 'Personal Blog and Magazine',
        'trending_news': [
            {
                'title': 'Apple opens its iPhone ecosystem in the EU',
                'author': 'Elon Mask',
                'date': '14 Jan, 2024',
                'image': 'img/blog/01.jpg'
            },
            {
                'title': 'EU could approve Apple\'s tap and go payment proposal',
                'author': 'Elon Mask',
                'date': '14 Jan, 2024',
                'image': 'img/blog/02.jpg'
            },
            {
                'title': 'Building an Editor by Sharing Code Between Android',
                'author': 'Elon Mask',
                'date': '14 Jan, 2024',
                'image': 'img/blog/03.jpg'
            },
            {
                'title': 'Google merges Android and Hardware divisions to drive AI',
                'author': 'Elon Mask',
                'date': '14 Jan, 2024',
                'image': 'img/blog/04.jpg'
            }
        ]
    }
    return render(request, 'index.html', context)

def author(request):
    """Author page view for the glrdesign app"""
    context = {
        'page_title': 'Author - Personal Blog and Magazine',
        'author': {
            'name': 'John Doe',
            'bio': 'A passionate writer and technology enthusiast',
            'posts_count': 25,
            'followers': 1200
        }
    }
    return render(request, 'author.html', context)

def blog_details(request):
    """Blog details page view for the glrdesign app"""
    context = {
        'page_title': 'Blog Details - Personal Blog and Magazine',
        'post': {
            'title': 'Sample Blog Post Title',
            'author': 'Jane Smith',
            'date': '15 Jan, 2024',
            'content': 'This is a sample blog post content...'
        }
    }
    return render(request, 'blog-details.html', context)

def column_layout_grid(request):
    """Column layout grid page view for the glrdesign app"""
    context = {
        'page_title': 'Column Layout Grid - Personal Blog and Magazine',
        'posts': [
            {'title': 'Blog Post Title 1', 'category': 'Technology'},
            {'title': 'Blog Post Title 2', 'category': 'Business'},
            {'title': 'Blog Post Title 3', 'category': 'Lifestyle'},
        ]
    }
    return render(request, 'column-layout-grid.html', context)

def coming_soon(request):
    """Coming soon page view for the glrdesign app"""
    context = {
        'page_title': 'Coming Soon - Personal Blog and Magazine',
        'launch_date': '30 days from now'
    }
    return render(request, 'coming-soon.html', context)

def error(request):
    """404 error page view for the glrdesign app"""
    context = {
        'page_title': '404 Error - Page Not Found',
        'error_code': '404'
    }
    return render(request, 'error.html', context)


def about_us(request):
    """About us page view for the glrdesign app"""
    context = {
        'page_title': 'About Us - Goal Line Report',
        'company': {
            'name': 'Goal Line Report',
            'founded': '2020',
            'mission': 'Providing comprehensive sports coverage to fans worldwide'
        }
    }
    return render(request, 'about-us.html', context)

def policy(request):
    """Policy page view for the glrdesign app"""
    context = {
        'page_title': 'Policies - Goal Line Report',
        'last_updated': 'January 15, 2024'
    }
    return render(request, 'policy.html', context)


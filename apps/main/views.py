from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from apps.story.models import Story
import json

def home(request):
    """Home page view showing featured stories with pagination"""
    stories = Story.objects.filter(status='published').order_by('-published_at')
    
    # Pagination: 6 stories per page
    paginator = Paginator(stories, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'Home',
        'page_title': 'Goal Line Report - Dashboard',
        'page_obj': page_obj,  # pass page_obj to template
    }
    return render(request, 'home.html', context)


def about(request):
    context = {
        'title': 'About',
        'page_title': 'About - Goal Line Report'
    }
    return render(request, 'about.html', context)


def reports(request):
    context = {
        'title': 'Reports',
        'page_title': 'Reports - Goal Line Report'
    }
    return render(request, 'reports.html', context)


def stories(request):
    return redirect('story:story_list')


@csrf_exempt
def api_example(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            return JsonResponse({
                'status': 'success',
                'message': 'Data received successfully',
                'data': data
            })
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Only POST method allowed'
    }, status=405)

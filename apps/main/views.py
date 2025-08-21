from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def home(request):
    """Home page view"""
    context = {
        'title': 'Home',
        'page_title': 'Goal Line Report - Dashboard'
    }
    return render(request, 'home.html', context)

def about(request):
    """About page view"""
    context = {
        'title': 'About',
        'page_title': 'About - Goal Line Report'
    }
    return render(request, 'about.html', context)

def reports(request):
    """Reports page view"""
    context = {
        'title': 'Reports',
        'page_title': 'Reports - Goal Line Report'
    }
    return render(request, 'reports.html', context)

def stories(request):
    """Stories page view - redirect to story app"""
    from django.shortcuts import redirect
    return redirect('story:story_list')

@csrf_exempt
def api_example(request):
    """Example API endpoint for AJAX calls"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Process the data here
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

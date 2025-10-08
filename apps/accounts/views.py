from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apps.story.models import Story
from .forms import CustomUserCreationForm
from apps.accounts.models import User

def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('story:column_layout_grid')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Account created for {user.username}!")
            # Check if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Account created for {user.username}!',
                    'redirect_url': '/'
                })
            return redirect('story:column_layout_grid')
        else:
            messages.error(request, "Please correct the errors below.")
            print(form.errors)  # Debug form errors
            # Check if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Please correct the errors below.',
                    'errors': form.errors
                }, status=400)
            return redirect('story:column_layout_grid')    
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('story:column_layout_grid')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Welcome back, {username}!',
                        'redirect_url': '/'
                    })
                return redirect('story:column_layout_grid')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid username or password.',
                    'errors': form.errors
                }, status=400)
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('story:column_layout_grid')

@login_required
def profile_view(request):
    """User profile view"""
    user = request.user
    profile = getattr(user, 'profile', None)
    is_editor = profile.is_editor if profile else False
    return render(request, "accounts/profile.html", {
        "is_editor": is_editor,
        "profile": profile,
        "author": user,
    })

def author_detail(request, username):
    """Author detail view"""
    author = get_object_or_404(User, username=username)
    stories = Story.objects.filter(author=author, status="published")
    context = {
        "author": author,
        "stories": stories,
    }
    return render(request, "author_detail.html", context)
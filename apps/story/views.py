from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
import json

from .models import Story, StoryChapter, StoryLike, StoryView

def story_list(request):
    """Display list of published stories"""
    stories = Story.objects.filter(status='published').select_related('author')
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        stories = stories.filter(
            Q(title__icontains=query) |
            Q(summary__icontains=query) |
            Q(tags__icontains=query) |
            Q(author__username__icontains=query)
        )
    
    # Filter by tags
    tag = request.GET.get('tag')
    if tag:
        stories = stories.filter(tags__icontains=tag)
    
    # Pagination
    paginator = Paginator(stories, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'tag': tag,
    }
    return render(request, 'story/story_list.html', context)

def story_detail(request, pk):
    """Display a single story"""
    story = get_object_or_404(Story, pk=pk)
    
    # Track view
    if request.user.is_authenticated:
        StoryView.objects.create(
            story=story,
            user=request.user,
            ip_address=request.META.get('REMOTE_ADDR')
        )
    else:
        StoryView.objects.create(
            story=story,
            ip_address=request.META.get('REMOTE_ADDR')
        )
    
    # Update view count
    story.views_count = story.story_views.count()
    story.save()
    
    # Check if user liked the story
    user_liked = False
    if request.user.is_authenticated:
        user_liked = story.story_likes.filter(user=request.user).exists()
    
    context = {
        'story': story,
        'user_liked': user_liked,
        'chapters': story.chapters.all(),
    }
    return render(request, 'story/story_detail.html', context)

@login_required
def story_create(request):
    """Create a new story"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title')
            content = data.get('content')
            summary = data.get('summary', '')
            tags = data.get('tags', '')
            status = data.get('status', 'draft')
            
            if not all([title, content]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Title and content are required'
                }, status=400)
            
            story = Story.objects.create(
                title=title,
                content=content,
                summary=summary,
                tags=tags,
                status=status,
                author=request.user
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Story created successfully',
                'story_id': story.id,
                'redirect_url': story.get_absolute_url()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return render(request, 'story/story_form.html')

@login_required
def story_edit(request, pk):
    """Edit an existing story"""
    story = get_object_or_404(Story, pk=pk, author=request.user)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title')
            content = data.get('content')
            summary = data.get('summary', '')
            tags = data.get('tags', '')
            status = data.get('status', story.status)
            
            if not all([title, content]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Title and content are required'
                }, status=400)
            
            story.title = title
            story.content = content
            story.summary = summary
            story.tags = tags
            story.status = status
            story.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Story updated successfully',
                'story_id': story.id
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    context = {
        'story': story,
        'is_edit': True
    }
    return render(request, 'story/story_form.html', context)

@login_required
def story_delete(request, pk):
    """Delete a story"""
    story = get_object_or_404(Story, pk=pk, author=request.user)
    
    if request.method == 'POST':
        story.delete()
        messages.success(request, 'Story deleted successfully.')
        return redirect('story:story_list')
    
    context = {
        'story': story
    }
    return render(request, 'story/story_confirm_delete.html', context)

@login_required
def like_story(request, pk):
    """Like or unlike a story"""
    story = get_object_or_404(Story, pk=pk)
    
    if request.method == 'POST':
        like, created = StoryLike.objects.get_or_create(
            story=story,
            user=request.user
        )
        
        if not created:
            # Unlike
            like.delete()
            action = 'unliked'
        else:
            action = 'liked'
        
        # Update likes count
        story.likes_count = story.story_likes.count()
        story.save()
        
        return JsonResponse({
            'status': 'success',
            'action': action,
            'likes_count': story.likes_count
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Only POST method allowed'
    }, status=405)

@login_required
def my_stories(request):
    """Display user's own stories"""
    stories = Story.objects.filter(author=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(stories, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'story/my_stories.html', context)

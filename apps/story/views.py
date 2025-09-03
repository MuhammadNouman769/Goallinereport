from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
import json

from .models import Story, StoryChapter, StoryLike, StoryView, StoryTag
from django.utils.text import slugify

def is_editor(user):
    """Check if user is an editor or chief editor"""
    return user.is_authenticated and user.profile.is_editor

def is_chief_editor(user):
    """Check if user is a chief editor"""
    return user.is_authenticated and user.profile.is_chief_editor

def story_list(request):
    """Display list of published stories"""
    # Only show published stories to everyone
    stories = Story.objects.filter(status='published').select_related('author')
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        stories = stories.filter(
            Q(title__icontains=query) |
            Q(summary__icontains=query) |
            Q(author__username__icontains=query)
        )
    
    # Filter by tags
    tag = request.GET.get('tag')
    if tag:
        stories = stories.filter(tags__name__icontains=tag)
    
    # Pagination
    paginator = Paginator(stories, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'tag': tag,
    }
    return render(request, 'story/story_list.html', context)

def story_detail(request, slug):
    """Display a single story"""
    story = get_object_or_404(Story, slug=slug)
    
    # Check if user can view this story
    if not story.can_view(request.user):
        messages.error(request, 'You do not have permission to view this story.')
        return redirect('story:story_list')
    
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
@user_passes_test(is_editor)
def story_create(request):
    """Create a new story"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title')
            content = data.get('content')
            summary = data.get('summary', '')
            tags = data.get('tags', [])
            status = data.get('status', 'draft')
            
            if not all([title, content]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Title and content are required'
                }, status=400)
            
            # Only chief editors can set status to published
            if status == 'published' and not request.user.profile.is_chief_editor:
                status = 'draft'
            
            story = Story.objects.create(
                title=title,
                content=content,
                summary=summary,
                status=status,
                author=request.user
            )
            
            # Add tags
            for tag_name in tags:
                tag, created = StoryTag.objects.get_or_create(
                    name=tag_name,
                    defaults={'slug': slugify(tag_name)}
                )
                story.tags.add(tag)
            
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
def story_edit(request, slug):
    """Edit an existing story"""
    story = get_object_or_404(Story, slug=slug)
    
    # Check if user can edit this story
    if not story.can_edit(request.user):
        messages.error(request, 'You do not have permission to edit this story.')
        return redirect('story:story_list')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title')
            content = data.get('content')
            summary = data.get('summary', '')
            tags = data.get('tags', [])
            status = data.get('status', story.status)
            
            if not all([title, content]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Title and content are required'
                }, status=400)
            
            # Only chief editors can set status to published
            if status == 'published' and not request.user.profile.is_chief_editor:
                status = 'draft'
            
            story.title = title
            story.content = content
            story.summary = summary
            story.status = status
            story.save()
            
            # Update tags
            story.tags.clear()
            for tag_name in tags:
                tag, created = StoryTag.objects.get_or_create(
                    name=tag_name,
                    defaults={'slug': slugify(tag_name)}
                )
                story.tags.add(tag)
            
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
def story_delete(request, slug):
    """Delete a story"""
    story = get_object_or_404(Story, slug=slug)
    
    # Check if user can edit this story
    if not story.can_edit(request.user):
        messages.error(request, 'You do not have permission to delete this story.')
        return redirect('story:story_list')
    
    if request.method == 'POST':
        story.delete()
        messages.success(request, 'Story deleted successfully.')
        return redirect('story:story_list')
    
    context = {
        'story': story
    }
    return render(request, 'story/story_confirm_delete.html', context)

@login_required
def like_story(request, slug):
    """Like or unlike a story"""
    story = get_object_or_404(Story, slug=slug)
    
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
@user_passes_test(is_editor)
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

@login_required
@user_passes_test(is_chief_editor)
def review_stories(request):
    """Display stories pending review for chief editors"""
    stories = Story.objects.filter(status='review').select_related('author').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(stories, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'story/review_stories.html', context)

@login_required
@user_passes_test(is_chief_editor)
def review_story(request, slug):
    """Review a specific story"""
    story = get_object_or_404(Story, slug=slug, status='review')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        review_notes = request.POST.get('review_notes', '')
        
        if action == 'approve':
            story.status = 'published'
            story.published_at = timezone.now()
            messages.success(request, 'Story approved and published successfully.')
        elif action == 'reject':
            story.status = 'rejected'
            messages.warning(request, 'Story rejected.')
        else:
            messages.error(request, 'Invalid action.')
            return redirect('story:review_stories')
        
        story.reviewed_by = request.user
        story.reviewed_at = timezone.now()
        story.review_notes = review_notes
        story.save()
        
        return redirect('story:review_stories')
    
    context = {
        'story': story,
        'chapters': story.chapters.all(),
    }
    return render(request, 'story/review_story.html', context)

@login_required
@user_passes_test(is_editor)
def submit_for_review(request, slug):
    """Submit a story for review"""
    story = get_object_or_404(Story, slug=slug, author=request.user)
    
    if story.status != 'draft':
        messages.error(request, 'Only draft stories can be submitted for review.')
        return redirect('story:my_stories')
    
    story.status = 'review'
    story.save()
    
    messages.success(request, 'Story submitted for review successfully.')
    return redirect('story:my_stories')



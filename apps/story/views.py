from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json
import logging
from django.template.loader import render_to_string
from .forms import StoryForm, StoryChapterForm, StoryChapterFormSet
from .models import Story, StoryChapter, StoryLike, StoryView, StoryTag
from apps.subscriptions.forms import SubscriptionForm  # Add this import

logger = logging.getLogger(__name__)

# Helper functions for permissions
def is_editor(user):
    """Check if user is an editor but not chief editor"""
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.is_editor and not user.profile.is_chief_editor

def is_chief_editor(user):
    """Check if user is a chief editor"""
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.is_chief_editor

# Story preview (frontend, for editors to view drafts)
@login_required
def story_preview(request, story_id):
    """Preview a story before publishing (frontend)"""
    story = get_object_or_404(Story, id=story_id)
    if not story.can_view(request.user):
        messages.error(request, "You do not have permission to view this story.")
        return redirect('story:column_layout_grid')
    return render(request, 'blog-detail.html', {'story': story, 'chapters': story.chapters.all()})

# Story delete (frontend, redirects to admin for editors)
@login_required
def story_delete(request, slug):
    """Delete a draft story (redirects to admin for editors)"""
    story = get_object_or_404(Story, slug=slug)
    if story.can_edit(request.user) and story.status == 'draft':
        return redirect(f'/admin/story/story/{story.id}/delete/')
    messages.error(request, "You do not have permission to delete this story.")
    return redirect('story:column_layout_grid')

# Public-facing story details view
def blog_details(request, slug):
    """Display a single published story with related content"""
    story = get_object_or_404(Story, slug=slug)
    
    if not story.can_view(request.user):
        messages.error(request, 'You do not have permission to view this story.')
        return redirect('story:column_layout_grid')
    
    # Track view
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
            user=None,  
            ip_address=request.META.get('REMOTE_ADDR')
        )

    
    story.views_count = story.story_views.count()
    story.save(update_fields=["views_count"])
    
    user_liked = False
    if request.user.is_authenticated:
        user_liked = story.story_likes.filter(user=request.user).exists()
    
    top_tags = StoryTag.objects.filter(
        stories__status='published'
    ).annotate(
        story_count=Count('stories')
    ).order_by('-story_count')[:3]
    
    featured_post = Story.objects.filter(
        status='published'
    ).select_related('author').order_by('?').first()

    stories = Story.objects.filter(status='published').order_by('-published_at')
    paginator = Paginator(stories, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    excluded_ids = (
        ([featured_post.id] if featured_post else []) +
        [story.id for story in page_obj]
    )
    popular_posts = Story.objects.filter(
        status='published'
    ).exclude(id__in=excluded_ids).select_related('author').order_by('-views_count')[:4]
    
    recommended_stories = []
    if request.user.is_authenticated:
        recommended_stories = Story.objects.filter(
            Q(status='published') & (
                Q(story_likes__user=request.user) | Q(story_views__user=request.user)
            )
        ).select_related('author').distinct().order_by('-published_at')[:4]
    
    if not recommended_stories:
        recommended_stories = Story.objects.filter(
            status='published'
        ).exclude(
            id=story.id
        ).select_related('author').order_by('-views_count')[:4]
    
    logger.info("Blog Details - Story: %s, Published: %s", story.title, story.status)
    logger.info("Top tags: %s", list(top_tags.values('name', 'story_count')))
    logger.info("Featured post: %s", featured_post.title if featured_post else "None")
    logger.info("All published stories count: %s", stories.count())
    logger.info("Popular posts count: %s", popular_posts.count())
    logger.info("Recommended stories count: %s", recommended_stories.count())
    if not top_tags:
        logger.warning("No tags found for published stories. Checking all tags:")
        all_tags = StoryTag.objects.annotate(story_count=Count('stories')).order_by('-story_count')[:5]
        for tag in all_tags:
            published_stories = tag.stories.filter(status='published').count()
            total_stories = tag.stories.count()
            logger.info("Tag: %s, Published Stories: %s, Total Stories: %s", tag.name, published_stories, total_stories)

    context = {
        'story': story,
        'user_liked': user_liked,
        'author': story.author,
        'featured_post': featured_post,
        'popular_posts': popular_posts,
        'top_tags': top_tags,
        'chapters': story.chapters.all(),
        'page_obj': page_obj,
        'recommended_stories': recommended_stories,
        'form': SubscriptionForm(),
    }
    return render(request, 'blog-details.html', context)

# Story creation (redirects to admin)
@csrf_exempt
@login_required
@user_passes_test(is_editor)
def story_create(request):
    """Redirect editors to Django admin panel for story creation"""
    return redirect('/admin/story/story/add/')

# Story editing (redirects to admin)
@csrf_exempt
@login_required
def story_edit(request, slug):
    """Redirect editors to Django admin panel for story editing"""
    story = get_object_or_404(Story, slug=slug)
    if story.can_edit(request.user):
        return redirect(f'/admin/story/story/{story.id}/change/')
    messages.error(request, 'You do not have permission to edit this story.')
    return redirect('story:column_layout_grid')



# Public-facing story listing with filtersfrom django.template.loader import render_to_string

def column_layout_grid(request, tag_slug=None):
    """Display list of published stories with filters (AJAX returns only cards)."""
    banner_stories = Story.objects.filter(
        status='published',
        story_banner__isnull=False
    ).select_related('author').order_by('-published_at')[:3]

    stories = Story.objects.filter(status='published').select_related('author')

    # Search filter
    query = request.GET.get('q')
    if query:
        stories = stories.filter(
            Q(title__icontains=query) |
            Q(summary__icontains=query) |
            Q(author__first_name__icontains=query) |
            Q(author__last_name__icontains=query) |
            Q(author__username__icontains=query)
        )

    # Category filter
    category = request.GET.get('category')
    if category == "latest":
        stories = stories.order_by('-created_at')
    elif category == "transfer":
        stories = stories.filter(title__icontains="transfer news")
    elif category == "reports":
        stories = stories.filter(title__icontains="match reports")
    elif category:
        stories = stories.filter(
            Q(title__icontains=category) |
            Q(tags__name__icontains=category)
        )

    # Tag filter
    tag = None
    if tag_slug:
        tag = get_object_or_404(StoryTag, slug=tag_slug)
        stories = stories.filter(tags=tag).distinct()

    stories = stories.distinct()

    # Pagination
    paginator = Paginator(stories, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # If AJAX: render only the partial with story cards (no header/footer/breadcrumb)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string(
            'partials/story_cards.html',
            {'page_obj': page_obj, 'tag': tag},
            request=request
        )
        # build next_page_url (preserve filters)
        next_page_url = None
        if page_obj.has_next():
            params = request.GET.copy()
            params['page'] = page_obj.next_page_number()
            next_page_url = f"{request.path}?{params.urlencode()}"

        return JsonResponse({
            'html': html,
            'has_next': page_obj.has_next(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
            'next_page_url': next_page_url,
        })

    # Normal full page render (header/footer/breadcrumb present)
    next_page_url = None
    if page_obj.has_next():
        params = request.GET.copy()
        params['page'] = page_obj.next_page_number()
        next_page_url = f"{request.path}?{params.urlencode()}"

    context = {
        'page_obj': page_obj,
        'query': query,
        'tag': tag,
        'category': category,
        'banner_stories': banner_stories,
        'next_page_url': next_page_url,
        'ajax': False,
    }
    return render(request, 'column-layout-grid.html', context)


# Story like/unlike interaction
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
            like.delete()
            action = 'unliked'
        else:
            action = 'liked'
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

# Editor's story management (redirects to admin)
@login_required
@user_passes_test(is_editor)
def my_stories(request):
    """Redirect editors to admin panel for viewing their stories"""
    return redirect('/admin/story/story/')

# Chief editor's review management (redirects to admin)
@login_required
@user_passes_test(is_chief_editor)
def review_stories(request):
    """Redirect chief editors to admin panel for reviewing stories"""
    return redirect('/admin/story/story/')

# Chief editor's specific story review (redirects to admin)
@login_required
@user_passes_test(is_chief_editor)
def review_story(request, slug):
    """Redirect chief editors to admin panel for reviewing a specific story"""
    story = get_object_or_404(Story, slug=slug, status='review')
    return redirect(f'/admin/story/story/{story.id}/change/')

# Editor's submit for review (redirects to admin)
@login_required
@user_passes_test(is_editor)
def submit_for_review(request, slug):
    """Redirect to admin panel for submitting story for review"""
    story = get_object_or_404(Story, slug=slug, author=request.user)
    if story.status == 'draft':
        return redirect(f'/admin/story/story/{story.id}/submit-for-review/')
    messages.error(request, 'Only draft stories can be submitted for review.')
    return redirect('story:my_stories')
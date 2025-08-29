"""===== Imports ====="""
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
import json
from .models import Story, StoryChapter, StoryLike, StoryView, StoryTag
from django.utils.text import slugify

"""===== Editor Checks ====="""
def is_editor(user):
    """Check if user is an editor or chief editor"""
    return user.is_authenticated and user.profile.is_editor

def is_chief_editor(user):
    """Check if user is a chief editor"""
    return user.is_authenticated and user.profile.is_chief_editor

"""===== Story List (All Stories) ====="""
def story_list(request):
    """Display list of published stories with search and tag filters"""
    stories = Story.objects.filter(status='published').select_related('author')

    query = request.GET.get('q', '')
    title_keyword = request.GET.get('title', '')
    search_query = request.GET.get('search', '')
    tag_query = request.GET.get('tag', '')

    # Search filter
    if query:
        stories = stories.filter(
            Q(title__icontains=query) |
            Q(summary__icontains=query) |
            Q(author__username__icontains=query)
        )
    elif search_query:
        stories = stories.filter(title__icontains=search_query)
        tag_query = search_query

    if tag_query and tag_query.lower() != "all":
        stories = stories.filter(title__icontains=tag_query)
        search_query = tag_query

    if title_keyword:
        stories = stories.filter(title__icontains=title_keyword)

    context = {
        'stories': stories,
        'query': query,
        'title_keyword': title_keyword,
        'search_query': search_query,
        'tag_query': tag_query,
        'tags': ["All", "Captures", "IPL", "Premier", "Super League"]
    }
    return render(request, 'story/story_list.html', context)

"""===== Story Detail ====="""
def story_detail(request, slug):
    """Display single story with view tracking and like status"""
    story = get_object_or_404(Story, slug=slug)

    if not story.can_view(request.user):
        messages.error(request, 'You do not have permission to view this story.')
        return redirect('story:story_list')

    # Track view
    StoryView.objects.create(
        story=story,
        user=request.user if request.user.is_authenticated else None,
        ip_address=request.META.get('REMOTE_ADDR')
    )

    # Update view count
    story.views_count = StoryView.objects.filter(story=story).count()
    story.save(update_fields=['views_count'])

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

"""===== Story Create ====="""
@login_required
@user_passes_test(is_editor)
def story_create(request):
    """Create a new story (draft or review, only chief editor can publish)"""
    if request.method == 'POST':
        try:
            if request.content_type == "application/json":
                data = json.loads(request.body)
            else:
                data = request.POST

            title = data.get('title')
            content = data.get('content')
            summary = data.get('summary', '')
            tags = data.get('tags', [])
            status = data.get('status', 'draft')

            if not all([title, content]):
                return JsonResponse({'status': 'error', 'message': 'Title and content are required'}, status=400)

            if status == 'published' and not request.user.profile.is_chief_editor:
                status = 'draft'

            # Slug handling
            base_slug = slugify(title)
            slug = base_slug
            counter = 1
            while Story.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            story = Story.objects.create(
                title=title,
                slug=slug,
                content=content,
                summary=summary,
                status=status,
                author=request.user
            )

            for tag_name in tags:
                tag, _ = StoryTag.objects.get_or_create(
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
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return render(request, 'story/story_form.html')

"""===== Story Edit ====="""
@login_required
def story_edit(request, slug):
    """Edit existing story"""
    story = get_object_or_404(Story, slug=slug)

    if not story.can_edit(request.user):
        messages.error(request, 'You do not have permission to edit this story.')
        return redirect('story:story_list')

    if request.method == 'POST':
        try:
            if request.content_type == "application/json":
                data = json.loads(request.body)
            else:
                data = request.POST

            title = data.get('title')
            content = data.get('content')
            summary = data.get('summary', '')
            tags = data.get('tags', [])
            status = data.get('status', story.status)

            if not all([title, content]):
                return JsonResponse({'status': 'error', 'message': 'Title and content are required'}, status=400)

            if status == 'published' and not request.user.profile.is_chief_editor:
                status = 'draft'

            # Slug handling
            base_slug = slugify(title)
            slug = story.slug
            if story.title != title:  # title changed
                counter = 1
                while Story.objects.filter(slug=slug).exclude(id=story.id).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                story.slug = slug

            story.title = title
            story.content = content
            story.summary = summary
            story.status = status
            story.save()

            story.tags.clear()
            for tag_name in tags:
                tag, _ = StoryTag.objects.get_or_create(
                    name=tag_name,
                    defaults={'slug': slugify(tag_name)}
                )
                story.tags.add(tag)

            return JsonResponse({'status': 'success', 'message': 'Story updated successfully', 'story_id': story.id})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    context = {'story': story, 'is_edit': True}
    return render(request, 'story/story_form.html', context)

"""===== Story Delete ====="""
@login_required
def story_delete(request, slug):
    """Delete a story"""
    story = get_object_or_404(Story, slug=slug)

    if not story.can_edit(request.user):
        messages.error(request, 'You do not have permission to delete this story.')
        return redirect('story:story_list')

    if request.method == 'POST':
        story.delete()
        messages.success(request, 'Story deleted successfully.')
        return redirect('story:story_list')

    context = {'story': story}
    return render(request, 'story/story_confirm_delete.html', context)

"""===== Like/Unlike Story ====="""
@login_required
def like_story(request, slug):
    """Like or unlike a story"""
    story = get_object_or_404(Story, slug=slug)

    if request.method == 'POST':
        like, created = StoryLike.objects.get_or_create(story=story, user=request.user)
        action = 'liked' if created else 'unliked'
        if not created:
            like.delete()

        story.likes_count = StoryLike.objects.filter(story=story).count()
        story.save(update_fields=['likes_count'])

        return JsonResponse({'status': 'success', 'action': action, 'likes_count': story.likes_count})

    return JsonResponse({'status': 'error', 'message': 'Only POST method allowed'}, status=405)

"""===== My Stories ====="""
@login_required
@user_passes_test(is_editor)
def my_stories(request):
    """Display stories created by the logged-in editor"""
    stories = Story.objects.filter(author=request.user).order_by('-created_at')
    context = {'stories': stories}
    return render(request, 'story/my_stories.html', context)

"""===== Submit Story for Review ====="""
@login_required
@user_passes_test(is_editor)
def submit_for_review(request, slug):
    """Editor submits story for chief editor review"""
    story = get_object_or_404(Story, slug=slug, author=request.user)

    if story.status != 'draft':
        messages.error(request, 'Only draft stories can be submitted for review.')
        return redirect('story:my_stories')

    story.status = 'review'
    story.save(update_fields=['status'])
    messages.success(request, 'Story submitted for review successfully.')
    return redirect('story:my_stories')

"""===== Review Stories ====="""
@login_required
@user_passes_test(is_chief_editor)
def review_stories(request):
    """Chief editor sees all stories pending review"""
    stories = Story.objects.filter(status='review').select_related('author').order_by('-created_at')
    context = {'stories': stories}
    return render(request, 'story/review_stories.html', context)

"""===== Review Single Story ====="""
@login_required
@user_passes_test(is_chief_editor)
def review_story(request, slug):
    """Chief editor approves or rejects a story"""
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

    context = {'story': story, 'chapters': story.chapters.all()}
    return render(request, 'story/review_story.html', context)

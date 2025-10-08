"""=================IMPORTS================"""
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from apps.story.models import Story, StoryTag, StoryView
from django.db.models import Q,Count
import json
import random
import logging
from datetime import timedelta
from django.utils import timezone
from apps.subscriptions.forms import SubscriptionForm  # Add this import
logger = logging.getLogger(__name__)

def home(request):
    """Home page view showing featured stories with pagination"""
    # Last week datetime (7 days ago)
    one_week_ago = timezone.now() - timedelta(days=7)
    
    banner_stories = (
    Story.objects.filter(
        status='published'
    )
    .exclude(story_banner='')       
    .exclude(story_banner__isnull=True)  
    .select_related('author')
    .order_by('-published_at')[:3]
)


    # Fetch trending stories: Latest 10 published stories
    trending_stories = Story.objects.filter(
        status='published'
    ).select_related('author').order_by('-published_at', '-views_count')[:10]

    # Fetch latest 4 Premier League stories (looser filter)
    premier_league_stories = Story.objects.filter(
        Q(status='published') &
        (Q(tags__name__icontains='premier') | Q(title__icontains='premier'))
    ).select_related('author').distinct().order_by('-published_at')[:4]
    
    # Fetch top 3 tags with the most published stories 
    top_tags = StoryTag.objects.filter(
        stories__status='published'
    ).annotate(
        story_count=Count('stories')
    ).order_by('-story_count')[:3]
    
    # Fetch a random published story for Featured Post
    featured_post = Story.objects.filter(
        status='published'
    ).select_related('author').order_by('?').first()

    # All stories with pagination
    stories = Story.objects.filter(status='published').order_by('-published_at')
    paginator = Paginator(stories, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Fetch popular posts: Top 4 most-viewed stories from last week, excluding those in other sections
    excluded_ids = (
        [story.id for story in banner_stories] +
        [story.id for story in trending_stories] +
        [story.id for story in premier_league_stories] +
        [featured_post.id] if featured_post else [] +
        [story.id for story in page_obj]
    )
    popular_posts = Story.objects.filter(
        status='published'
    ).exclude(id__in=excluded_ids).select_related('author').annotate(
        weekly_views=Count('story_views', filter=Q(story_views__created_at__gte=one_week_ago))
    ).order_by('-weekly_views')[:4]
    

    # Daily view count query for database display
    daily_views = StoryView.objects.filter(created_at__gte=one_week_ago).values(
        'story__title', 
        'created_at__date'
    ).annotate(
        total_views=Count('id')
    ).order_by('story__title', 'created_at__date')

    # Fetch latest news: Stories with "Latest News" tag or "latest" or "news" in title, paginated
    latest_news = Story.objects.filter(
        Q(status='published') &
        (Q(tags__name__iexact='Latest News') | Q(title__icontains='latest news') | Q(title__icontains=' latest news'))
    ).select_related('author').prefetch_related('tags').distinct().order_by('-published_at')
    latest_news_paginator = Paginator(latest_news, 3)  # 3 stories per page
    latest_news_page_number = request.GET.get('latest_news_page', 1)
    latest_news_page_obj = latest_news_paginator.get_page(latest_news_page_number)
    
    
# Debug prints (remove after testing)
    print("Premier League stories count:", premier_league_stories.count())
    print("Tags with premier:", list(StoryTag.objects.filter(name__icontains='premier').values_list('name', flat=True)))
    print("Featured post:", featured_post.title if featured_post else "None")
    print("All published stories count:", Story.objects.filter(status='published').count())
    print("Popular posts count:", popular_posts.count())
    print("Latest news count:", latest_news.count())
    print("Top tags:", list(top_tags.values('name', 'story_count')))

    context = {
        'title': 'Home',
        'page_title': 'Goal Line Report - Dashboard',
        'page_obj': page_obj,
        'banner_stories': banner_stories,
        'trending_stories': trending_stories,
        'premier_league_stories': premier_league_stories,
        'featured_post': featured_post,
        'popular_posts': popular_posts,
        'latest_news_page_obj': latest_news_page_obj,
        'latest_news_page_number': int(latest_news_page_number),
        'top_tags': top_tags,  # Add top tags to context
        'form': SubscriptionForm(),
        'daily_views': daily_views,
    }
    return render(request, 'index.html', context)


def about(request):
    # context = {
    #     'title': 'About',
    #     'page_title': 'About - Goal Line Report'
    # }
    return render(request, 'about-us.html')

def reports(request):
    context = {
        'title': 'Reports',
        'page_title': 'Reports - Goal Line Report'
    }
    return render(request, 'reports.html', context)

# def stories(request):
#     return redirect('story:column_layout_grid')

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
from django.urls import path
from . import views

app_name = 'rss_feeds'

urlpatterns = [
    # Main feed views
    path('', views.rss_feed_list, name='feed_list'),
    path('feed/<uuid:feed_id>/', views.rss_feed_detail, name='feed_detail'),
    
    # Management views (require login)
    path('sources/', views.rss_feed_sources, name='sources'),
    path('stats/', views.rss_feed_stats, name='stats'),
    
    # AJAX endpoints
    path('feed/<uuid:feed_id>/mark-read/', views.mark_as_read_ajax, name='mark_as_read'),
    path('feed/<uuid:feed_id>/archive/', views.archive_feed_ajax, name='archive_feed'),
    path('fetch/', views.fetch_feeds_ajax, name='fetch_feeds'),
    
    # API endpoint
    path('api/feeds/', views.rss_feed_api, name='feed_api'),
]

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import RSSFeedSource, RSSFeedItem, FeedFetchLog


@admin.register(RSSFeedSource)
class RSSFeedSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'source_type', 'feed_url', 'is_active', 'last_fetched', 'feed_count', 'created_at']
    list_filter = ['source_type', 'is_active', 'created_at']
    search_fields = ['name', 'feed_url']
    readonly_fields = ['last_fetched', 'created_at', 'updated_at']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'source_type', 'feed_url', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('last_fetched', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def feed_count(self, obj):
        """Display feed count with link to feed items"""
        count = obj.feed_count
        url = reverse('admin:rss_feeds_rssfeeditem_changelist') + f'?source__id__exact={obj.id}'
        return format_html('<a href="{}">{} items</a>', url, count)
    feed_count.short_description = 'Feed Items'


@admin.register(RSSFeedItem)
class RSSFeedItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'source', 'author', 'published_date', 'is_read', 'is_archived', 'fetched_at']
    list_filter = ['source', 'is_read', 'is_archived', 'published_date', 'fetched_at', 'category']
    search_fields = ['title', 'description', 'author', 'category']
    readonly_fields = ['fetched_at', 'guid']
    list_editable = ['is_read', 'is_archived']
    date_hierarchy = 'published_date'
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'description', 'content', 'link', 'author', 'category')
        }),
        ('Metadata', {
            'fields': ('source', 'guid', 'published_date', 'fetched_at')
        }),
        ('Status', {
            'fields': ('is_read', 'is_archived')
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('source')
    
    def short_title(self, obj):
        """Display truncated title"""
        return obj.short_title
    short_title.short_description = 'Title'
    
    def short_description(self, obj):
        """Display truncated description"""
        return obj.short_description
    short_description.short_description = 'Description'


@admin.register(FeedFetchLog)
class FeedFetchLogAdmin(admin.ModelAdmin):
    list_display = ['source', 'status', 'items_fetched', 'items_new', 'fetch_duration', 'created_at']
    list_filter = ['source', 'status', 'created_at']
    search_fields = ['source__name', 'error_message']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Fetch Information', {
            'fields': ('source', 'status', 'items_fetched', 'items_new', 'fetch_duration')
        }),
        ('Error Details', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('source')
    
    def has_add_permission(self, request):
        """Disable manual creation of fetch logs"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing of fetch logs"""
        return False

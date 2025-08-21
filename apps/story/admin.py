from django.contrib import admin
from .models import Story, StoryChapter, StoryLike, StoryView

class StoryChapterInline(admin.TabularInline):
    model = StoryChapter
    extra = 1
    fields = ['title', 'content', 'order']

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'created_at', 'published_at', 'views_count', 'likes_count']
    list_filter = ['status', 'created_at', 'published_at']
    search_fields = ['title', 'content', 'summary', 'author__username']
    date_hierarchy = 'created_at'
    list_editable = ['status']
    prepopulated_fields = {'summary': ('title',)}
    inlines = [StoryChapterInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'content', 'summary', 'author', 'status')
        }),
        ('Metadata', {
            'fields': ('tags', 'published_at'),
            'classes': ('collapse',)
        }),
        ('Engagement', {
            'fields': ('views_count', 'likes_count'),
            'classes': ('collapse',)
        }),
    )

@admin.register(StoryChapter)
class StoryChapterAdmin(admin.ModelAdmin):
    list_display = ['title', 'story', 'order', 'created_at']
    list_filter = ['created_at', 'story']
    search_fields = ['title', 'content', 'story__title']
    list_editable = ['order']
    ordering = ['story', 'order']

@admin.register(StoryLike)
class StoryLikeAdmin(admin.ModelAdmin):
    list_display = ['story', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['story__title', 'user__username']
    date_hierarchy = 'created_at'

@admin.register(StoryView)
class StoryViewAdmin(admin.ModelAdmin):
    list_display = ['story', 'user', 'ip_address', 'created_at']
    list_filter = ['created_at']
    search_fields = ['story__title', 'user__username', 'ip_address']
    date_hierarchy = 'created_at'

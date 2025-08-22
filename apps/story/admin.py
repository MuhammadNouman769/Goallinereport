from django.contrib import admin
from django.utils import timezone
from .models import Story, StoryChapter, StoryLike, StoryView

class StoryChapterInline(admin.TabularInline):
    model = StoryChapter
    extra = 1
    fields = ['title', 'content', 'order']

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'created_at', 'published_at', 'reviewed_by', 'views_count', 'likes_count']
    list_filter = ['status', 'created_at', 'published_at', 'reviewed_by']
    search_fields = ['title', 'content', 'summary', 'author__username', 'review_notes']
    date_hierarchy = 'created_at'
    list_editable = ['status']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [StoryChapterInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'content', 'summary', 'author', 'status')
        }),
        ('Tags', {
            'fields': ('tags',),
            'classes': ('collapse',)
        }),
        ('Review Workflow', {
            'fields': ('reviewed_by', 'reviewed_at', 'review_notes'),
            'classes': ('collapse',)
        }),
        ('Publishing', {
            'fields': ('published_at',),
            'classes': ('collapse',)
        }),
        ('Engagement', {
            'fields': ('views_count', 'likes_count'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data and obj.status == 'published':
            obj.published_at = timezone.now()
        if 'status' in form.changed_data and obj.status in ['published', 'rejected']:
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)

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

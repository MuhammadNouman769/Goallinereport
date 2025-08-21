from django.contrib import admin
from .models import Comment, CommentLike

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'story', 'created_at', 'is_active', 'is_reply']
    list_filter = ['is_active', 'created_at', 'story']
    search_fields = ['text', 'author__username', 'story__title']
    date_hierarchy = 'created_at'
    list_editable = ['is_active']
    
    def is_reply(self, obj):
        return obj.is_reply
    is_reply.boolean = True
    is_reply.short_description = 'Is Reply'

@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ['comment', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['comment__text', 'user__username']
    date_hierarchy = 'created_at'

from django.db import models
from django.contrib.auth.models import User
from apps.utils.models import CoreModel
from apps.story.models import Story

class Comment(CoreModel):
    """Comment model for stories"""
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    
    # For threaded comments
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return str(self.id)
    
    @property
    def is_reply(self):
        return self.parent is not None
    
    @property
    def replies_count(self):
        return self.replies.filter(is_active=True).count()

class CommentLike(CoreModel):
    """Model for tracking likes on comments"""
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['comment', 'user']
    
    def __str__(self):
        return str(self.id)

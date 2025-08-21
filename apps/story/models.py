from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from apps.utils.models import CoreModel

class Story(CoreModel):
    """Model for stories/News"""
    class StoryStatus(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        REVIEW = 'review', 'Review'
        PUBLISHED = 'published', 'Published'
        CANCELLED = 'cancelled', 'Cancelled'

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    status = models.CharField(max_length=20, choices=StoryStatus.choices, default=StoryStatus.DRAFT)
    
    # Story metadata
    summary = models.TextField(blank=True, help_text="Brief summary of the story")
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Engagement metrics
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)

    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Stories'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('story:story_detail', kwargs={'pk': self.pk})
    
    @property
    def is_published(self):
        return self.status == 'published'
    
    @property
    def tag_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

class StoryChapter(CoreModel):
    """Model for chapters within a story"""
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)
    
    
    class Meta:
        ordering = ['order', 'created_at']
        unique_together = ['story', 'order']
    
    def __str__(self):
        return f"{self.story.title} - Chapter {self.order}: {self.title}"

class StoryLike(CoreModel):
    """Model for tracking likes on stories"""
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='story_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['story', 'user']
    
    def __str__(self):
        return f'{self.user.username} likes {self.story.title}'

class StoryView(CoreModel):
    """Model for tracking story views"""
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='story_views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'View of {self.story.title} at {self.created_at}'

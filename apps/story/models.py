from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from apps.utils.models import CoreModel

class Story(CoreModel):
    """Model for stories/News"""
    class StoryStatus(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        REVIEW = 'review', 'Under Review'
        PUBLISHED = 'published', 'Published'
        REJECTED = 'rejected', 'Rejected'
        CANCELLED = 'cancelled', 'Cancelled'

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    status = models.CharField(max_length=20, choices=StoryStatus.choices, default=StoryStatus.DRAFT)
    tags = models.ManyToManyField("StoryTag", related_name='stories', blank=True)
    
    # Story metadata
    summary = models.TextField(blank=True, help_text="Brief summary of the story")
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Review workflow
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviewed_stories'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True, help_text="Review comments from chief editor")
    
    # Engagement metrics
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)

    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Stories'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    def can_edit(self, user):
        """Check if user can edit this story"""
        if not user.is_authenticated:
            return False
        if user.profile.is_chief_editor:
            return True
        return self.author == user and user.profile.is_editor
    
    def can_review(self, user):
        """Check if user can review this story"""
        return user.is_authenticated and user.profile.is_chief_editor
    
    def can_publish(self, user):
        """Check if user can publish this story"""
        return user.is_authenticated and user.profile.is_chief_editor
    
    def can_view(self, user):
        """Check if user can view this story"""
        if self.status == 'published':
            return True
        if not user.is_authenticated:
            return False
        if user.profile.is_chief_editor:
            return True
        return self.author == user
    
    def get_absolute_url(self):
        return reverse('story:story_detail', kwargs={'slug': self.slug})
    
    @property
    def is_published(self):
        return self.status == 'published'
    
    @property
    def tag_list(self):
        return self.tags.all()

class StoryChapter(CoreModel):
    """Model for chapters within a story"""
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='story_chapters/', null=True, blank=True)
    video = models.FileField(upload_to='story_chapters/', null=True, blank=True)
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



class StoryTag(CoreModel):
    """Model for tags for stories"""
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Story Tags'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from apps.utils.models import CoreModel


"""===== STORY MODEL ====="""
class Story(CoreModel):
    """Model for stories/News"""

    class StoryStatus(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        REVIEW = 'review', 'Under Review'
        PUBLISHED = 'published', 'Published'
        REJECTED = 'rejected', 'Rejected'
        CANCELLED = 'cancelled', 'Cancelled'

    # Core Fields
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='stories/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    status = models.CharField(max_length=20, choices=StoryStatus.choices, default=StoryStatus.DRAFT)
    tags = models.ManyToManyField("StoryTag", related_name='stories', blank=True)

    # Metadata
    summary = models.TextField(blank=True, help_text="Brief summary of the story")
    published_at = models.DateTimeField(null=True, blank=True)

    # Review Workflow
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_stories'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True, help_text="Review comments from chief editor")

    # Engagement Metrics
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)

    """--- META INFO ---"""
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Stories'

    """--- STRING REPRESENTATION ---"""
    def __str__(self):
        return self.title

    """--- SAVE HOOK ---"""
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == self.StoryStatus.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    """--- PERMISSIONS ---"""
    def can_edit(self, user):
        """Editor can edit only own stories, Chief Editor can edit all"""
        if not user.is_authenticated:
            return False
        if user.profile.is_chief_editor:
            return True
        return self.author == user and user.profile.is_editor

    def can_review(self, user):
        """Only Chief Editor can review"""
        return user.is_authenticated and user.profile.is_chief_editor

    def can_publish(self, user):
        """Only Chief Editor can publish"""
        return user.is_authenticated and user.profile.is_chief_editor

    def can_view(self, user):
        """Define story visibility"""
        if self.status == self.StoryStatus.PUBLISHED:
            return True
        if not user.is_authenticated:
            return False
        if user.profile.is_chief_editor:
            return True
        return self.author == user  # editor can view own drafts

    """--- UTILITIES ---"""
    def get_absolute_url(self):
        return reverse('story:story_detail', kwargs={'slug': self.slug})

    @property
    def is_published(self):
        return self.status == self.StoryStatus.PUBLISHED

    @property
    def tag_list(self):
        return self.tags.all()


"""===== STORY CHAPTER ====="""
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


"""===== STORY LIKE ====="""
class StoryLike(CoreModel):
    """Model for tracking likes on stories"""
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='story_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['story', 'user']

    def __str__(self):
        return f'{self.user.username} likes {self.story.title}'


"""===== STORY VIEW ====="""
class StoryView(CoreModel):
    """Model for tracking story views"""
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='story_views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'View of {self.story.title} at {self.created_at}'


"""===== STORY TAG ====="""
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

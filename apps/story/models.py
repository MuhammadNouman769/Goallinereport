from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from apps.utils.models import CoreModel
from ckeditor_uploader.fields import RichTextUploadingField


""" ----------------- Story Model -----------------"""
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
    content = RichTextUploadingField()
    image = models.ImageField(blank=True, null=True)
    story_banner = models.ImageField(upload_to='story_banner/',blank=True, null=True,
        help_text="banner image for the story (chief editor only)"
        )
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    status = models.CharField(max_length=20, choices=StoryStatus.choices, default=StoryStatus.DRAFT)
    tags = models.ManyToManyField("StoryTag", related_name='stories', blank=True)
    
    summary = models.TextField(blank=True, help_text="Brief summary of the story")
    published_at = models.DateTimeField(null=True, blank=True)
    
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviewed_stories'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True, help_text="Review comments from chief editor")
    
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
        if not user.is_authenticated:
            return False
        if hasattr(user, "profile") and getattr(user.profile, "is_chief_editor", False):
            return True
        return self.author == user and getattr(user.profile, "is_editor", False)
    
    def can_review(self, user):
        return user.is_authenticated and hasattr(user, "profile") and getattr(user.profile, "is_chief_editor", False)
    
    def can_publish(self, user):
        return user.is_authenticated and hasattr(user, "profile") and getattr(user.profile, "is_chief_editor", False)
    
    
    def can_edit_banner(self, user):
        """Check if user can edit the story_banner field"""
        return user.is_authenticated and hasattr (user, "profile") and user.profile.is_chief_editor
    
    def can_view(self, user):
        if self.status == 'published':
            return True
        if not user.is_authenticated:
            return False
        if hasattr(user, "profile") and getattr(user.profile, "is_chief_editor", False):
            return True
        return self.author == user
    
    def get_absolute_url(self):
        return reverse('story:blog_details', kwargs={'slug': self.slug})
    
    @property
    def is_published(self):
        return self.status == 'published'
    
    @property
    def tag_list(self):
        return self.tags.all()


""" ----------------- Story Chapter -----------------"""
class StoryChapter(CoreModel):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=200)
    content = RichTextUploadingField()
    image = models.ImageField(upload_to='story_chapters/', null=True, blank=True)
    video = models.FileField(upload_to='story_chapters/', null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'created_at']
        constraints = [
            models.UniqueConstraint(fields=['story', 'order'], name='unique_story_order')
        ]

    def __str__(self):
        return f"{self.story.title} - Chapter {self.order}: {self.title}"


"""----------------- Story Like -----------------"""
class StoryLike(CoreModel):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='story_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['story', 'user'],name='unique_story_user_like')
        ]

    def __str__(self):
        return f'{self.user.username} likes {self.story.title}'


""" ----------------- Story View -----------------"""
class StoryView(CoreModel):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='story_views')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'View of {self.story.title} at {self.created_at}'


"""----------------- Story Tag -----------------"""
class StoryTag(CoreModel):
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


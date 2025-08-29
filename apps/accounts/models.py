"""===== IMPORTS ====="""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.utils.models import CoreModel


"""===== USER PROFILE MODEL ====="""
class UserProfile(CoreModel):
    """Extended user profile with user type and additional fields"""

    """--- USER TYPES ---"""
    class UserType(models.TextChoices):
        CUSTOMER = 'customer', 'Customer / End User'
        EDITOR = 'editor', 'Editor'
        CHIEF_EDITOR = 'chief_editor', 'Chief Editor'

    """--- FIELDS ---"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.CUSTOMER
    )
    bio = models.TextField(blank=True, help_text="Brief description about the user")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)

    # Editor specific fields
    is_verified = models.BooleanField(default=False, help_text="Editor verification status")
    specialization = models.CharField(max_length=100, blank=True, help_text="Editor's area of expertise")

    """--- META INFO ---"""
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    """--- STRING REPRESENTATION ---"""
    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"

    """--- CUSTOM PROPERTIES ---"""
    @property
    def is_editor(self):
        return self.user_type in [self.UserType.EDITOR, self.UserType.CHIEF_EDITOR]

    @property
    def is_chief_editor(self):
        return self.user_type == self.UserType.CHIEF_EDITOR

    @property
    def can_publish(self):
        return self.user_type == self.UserType.CHIEF_EDITOR

    @property
    def can_review(self):
        return self.user_type == self.UserType.CHIEF_EDITOR


"""===== SIGNALS TO AUTO-CREATE/UPDATE PROFILE ====="""
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Create or update profile automatically when User is saved"""
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()

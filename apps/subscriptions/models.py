from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class Subscriber(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Use UUID as PK
    email = models.EmailField(unique=True)  # Enforce uniqueness on email
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='subscriptions')  # Optional user link
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def deactivate(self):
        self.is_active = False
        self.save()

    def __str__(self):
        return self.email
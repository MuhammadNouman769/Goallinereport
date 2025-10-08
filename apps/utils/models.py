from django.db import models
import uuid

# ----------------- Core Manager -----------------
class CoreManager(models.Manager):
    """Custom manager to filter active objects by default"""
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


# ----------------- Core Model -----------------
class CoreModel(models.Model):
    """Abstract base model with common fields and methods"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    objects = CoreManager()  # ✅ Custom manager

    class Meta:
        abstract = True  # ✅ This makes CoreModel reusable without creating a DB table

    def __str__(self):
        return str(self.id)  # UUID converted to string

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id}>"

    def activate(self):
        self.is_active = True
        self.save()

    def deactivate(self):
        self.is_active = False
        self.save()

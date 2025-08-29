"""===== IMPORTS ====="""
from django.contrib import admin, messages
from django.utils import timezone
from django.http import HttpResponseRedirect
from .models import Story, StoryChapter, StoryLike, StoryView, StoryTag


"""===== INLINE CHAPTERS ====="""
class StoryChapterInline(admin.TabularInline):
    model = StoryChapter
    extra = 1
    fields = ["title", "content", "order"]


"""===== STORY ADMIN ====="""
@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    change_form_template = "admin/story/story/change_form.html"

    """--- LIST / SEARCH ---"""
    list_display = ["title", "status", "created_at", "published_at", "reviewed_by", "views_count", "likes_count"]
    list_filter = ["status", "created_at", "published_at", "reviewed_by", "tags"]
    search_fields = ["title", "content", "summary", "review_notes"]
    date_hierarchy = "created_at"
    prepopulated_fields = {"slug": ("title",)}
    inlines = [StoryChapterInline]

    """--- FIELDSETS ---"""
    fieldsets = (
        ("=== Basic Information ===", {"fields": ("title", "slug", "image", "content", "summary", "status")}),
        ("=== Tags ===", {"fields": ("tags",), "classes": ("collapse",)}),
        ("=== Review Workflow ===", {"fields": ("reviewed_by", "reviewed_at", "review_notes"), "classes": ("collapse",)}),
        ("=== Publishing ===", {"fields": ("published_at",), "classes": ("collapse",)}),
        ("=== Engagement ===", {"fields": ("views_count", "likes_count"), "classes": ("collapse",)}),
    )

    """===== QUERYSET RULES ====="""
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        profile = getattr(request.user, "profile", None)

        if profile and profile.is_editor and not profile.is_chief_editor:
            return qs.filter(author=request.user)

        if profile and profile.is_chief_editor:
            return qs.exclude(status=Story.StoryStatus.DRAFT)

        return qs

    """===== PERMISSIONS ====="""
    def has_change_permission(self, request, obj=None):
        profile = getattr(request.user, "profile", None)
        if profile and profile.is_editor and not profile.is_chief_editor:
            if obj:
                return obj.author_id == request.user.id and obj.status == Story.StoryStatus.DRAFT
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        profile = getattr(request.user, "profile", None)
        if profile and profile.is_editor and not profile.is_chief_editor:
            if obj:
                return obj.author_id == request.user.id and obj.status == Story.StoryStatus.DRAFT
        return super().has_delete_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        profile = getattr(request.user, "profile", None)
        if profile and profile.is_editor and not profile.is_chief_editor:
            ro += ["status", "reviewed_by", "reviewed_at", "published_at"]
        return ro

    """===== SAVE HOOK ====="""
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.author = request.user

        profile = getattr(request.user, "profile", None)
        if profile and profile.is_chief_editor and "status" in getattr(form, "changed_data", []):
            if obj.status == Story.StoryStatus.PUBLISHED:
                obj.published_at = timezone.now()
            if obj.status in [Story.StoryStatus.PUBLISHED, Story.StoryStatus.REJECTED, Story.StoryStatus.CANCELLED]:
                obj.reviewed_by = request.user
                obj.reviewed_at = timezone.now()

        super().save_model(request, obj, form, change)

    """===== CUSTOM BUTTON ACTIONS ====="""
    def response_change(self, request, obj):
        profile = getattr(request.user, "profile", None)

        if "_saveasdraft" in request.POST:
            obj.status = Story.StoryStatus.DRAFT
            obj.save()
            self.message_user(request, "✅ Story saved as Draft.")
            return HttpResponseRedirect(".")

        if "_requestpublish" in request.POST:
            obj.status = Story.StoryStatus.REVIEW
            obj.reviewed_by = None
            obj.reviewed_at = None
            obj.save()
            self.message_user(request, "📤 Story submitted for review.")
            return HttpResponseRedirect("..")

        if profile and profile.is_chief_editor:
            if "_publish" in request.POST:
                obj.status = Story.StoryStatus.PUBLISHED
                obj.published_at = timezone.now()
                obj.reviewed_by = request.user
                obj.reviewed_at = timezone.now()
                obj.save()
                self.message_user(request, "✅ Story Published!")
                return HttpResponseRedirect("..")

            if "_reject" in request.POST:
                obj.status = Story.StoryStatus.REJECTED
                obj.reviewed_by = request.user
                obj.reviewed_at = timezone.now()
                obj.save()
                self.message_user(request, "❌ Story Rejected.")
                return HttpResponseRedirect("..")

            if "_cancel" in request.POST:
                obj.status = Story.StoryStatus.CANCELLED
                obj.reviewed_by = request.user
                obj.reviewed_at = timezone.now()
                obj.save()
                self.message_user(request, "🔄 Story Cancelled.")
                return HttpResponseRedirect("..")

            if "_delete" in request.POST:
                obj.delete()
                self.message_user(request, "🗑 Story Deleted.")
                return HttpResponseRedirect("../")

        return super().response_change(request, obj)

    """===== TEMPLATE CONTEXT ====="""
    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        ctx = extra_context or {}
        profile = getattr(request.user, "profile", None)
        ctx["is_editor"] = bool(profile and profile.is_editor and not profile.is_chief_editor)
        ctx["is_chief_editor"] = bool(profile and profile.is_chief_editor)
        return super().changeform_view(request, object_id, form_url, ctx)


"""===== STORY CHAPTER ADMIN ====="""
@admin.register(StoryChapter)
class StoryChapterAdmin(admin.ModelAdmin):
    list_display = ["title", "story", "order", "created_at"]
    list_editable = ["order"]
    ordering = ["story", "order"]


"""===== STORY LIKE ADMIN ====="""
@admin.register(StoryLike)
class StoryLikeAdmin(admin.ModelAdmin):
    list_display = ["story", "user", "created_at"]
    search_fields = ["story__title", "user__username"]


"""===== STORY VIEW ADMIN ====="""
@admin.register(StoryView)
class StoryViewAdmin(admin.ModelAdmin):
    list_display = ["story", "user", "ip_address", "created_at"]
    search_fields = ["story__title", "user__username", "ip_address"]


"""===== STORY TAG ADMIN ====="""
@admin.register(StoryTag)
class StoryTagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "created_at"]
    prepopulated_fields = {"slug": ("name",)}

from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils import timezone
from .models import Story, StoryChapter, StoryLike, StoryView, StoryTag
from .forms import StoryForm, StoryChapterFormSet
from django.db.models import Q, Count
from django.db.models.functions import TruncDate
from ckeditor.widgets import CKEditorWidget
from django import forms
from django.db import models
from django.db import transaction
from django.core.exceptions import PermissionDenied
# Inline for StoryChapter with restrictions (replace your current inline)
class StoryChapterInline(admin.StackedInline):
    model = StoryChapter
    extra = 1
    fields = ['title', 'image', 'video', 'order', 'content']
   
        

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'content':
            kwargs['widget'] = CKEditorWidget(attrs={'style': 'width: 700px; min-height: 300px;'})
        elif db_field.name in ('image', 'video'):
            kwargs['widget'] = forms.ClearableFileInput(attrs={'style': 'max-width: 150px; display: inline-block;'})
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    # Accept the parent 'obj' (Story instance) — important to avoid TypeError
    def has_change_permission(self, request, obj=None):
        # obj is the parent Story when shown inside the Story change form
        if obj and getattr(obj, 'status', None) != 'draft':
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and getattr(obj, 'status', None) != 'draft':
            return False
        return super().has_delete_permission(request, obj)

    def has_add_permission(self, request, obj=None):
        """
        obj: when editing a Story, Django passes the parent Story instance here.
        If obj is not provided (e.g. add-inline outside the story change form),
        try to read ?story=<id> from GET as a fallback.
        """
        story = obj
        if story is None:
            story_id = request.GET.get('story')
            if story_id:
                try:
                    story = Story.objects.get(pk=story_id)
                except Story.DoesNotExist:
                    story = None

        if story and getattr(story, 'status', None) != 'draft':
            return False

        # pass both args to super in case the base method expects the obj
        return super().has_add_permission(request, obj)


# Custom Form for Story Admin
class StoryAdminForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = '__all__'
        widgets = {
            'content': CKEditorWidget(config_name='default'),
        }


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'author',
        'status_text',   # 👈 custom method instead of "status"
        'created_at',
        'published_at',
        'reviewed_by',
        'views_count',
        'likes_count'
    ]
    list_filter = ['status','created_at', 'published_at', 'reviewed_by']
    search_fields = ['title', 'content', 'summary', 'author__username', 'review_notes']
    date_hierarchy = 'created_at'
    # list_editable = ['status']   👈 remove this line completely
    prepopulated_fields = {'slug': ('title',)}
    inlines = [StoryChapterInline]
    actions = ['submit_for_review']
    form = StoryAdminForm
    change_form_template = 'admin/story/story/change_form.html'
    def status_text(self, obj):
        return obj.get_status_display()   # readable text only

    status_text.short_description = "Status"



    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            ('Basic Information', {
                'fields': ('title', 'slug', 'tags', 'image', 'content', 'summary')
            }),
         
        )
        if request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_chief_editor):
            fieldsets[0][1]['fields'] = ('title', 'slug', 'image', 'story_banner', 'content', 'summary', 'author', 'status', 'tags')
        return fieldsets

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Superuser & Chief Editor -> sab stories
        if request.user.is_superuser or (
            hasattr(request.user, 'profile') and request.user.profile.is_chief_editor
        ):
            return qs

        # Editor -> sab stories dekh sakta hai
        if hasattr(request.user, 'profile') and request.user.profile.is_editor:
            return qs

        # Author -> sirf apni stories
        return qs.filter(author=request.user)


    def get_readonly_fields(self, request, obj=None):
        readonly_fields = []
        if obj and not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_chief_editor)):
            if obj.status != 'draft':
                readonly_fields = ['title', 'slug', 'image', 'content', 'summary', 'tags']
            if not obj.can_edit_banner(request.user):
                readonly_fields.append('story_banner')
        return readonly_fields


    def has_change_permission(self, request, obj=None):
        if not obj:
            return True

        # Superuser & Chief Editor -> sab kuch edit kar sakte hain
        if request.user.is_superuser or (
            hasattr(request.user, 'profile') and request.user.profile.is_chief_editor
        ):
            return True

        # Editor -> sirf draft edit kar sakta hai
        if hasattr(request.user, 'profile') and request.user.profile.is_editor:
            return obj.status == "draft"

        # Author -> apni draft edit kar sakta hai
        return obj.author == request.user and obj.status == "draft"


       

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('preview/<str:story_id>/', self.admin_site.admin_view(self.preview_story), name='story_preview'),
            path('<str:story_id>/submit-for-review/', self.admin_site.admin_view(self.submit_for_review_view), name='story_submit_for_review'),
            path('<str:story_id>/delete/', self.admin_site.admin_view(self.delete_view), name='story_delete'),
            path('<str:story_id>/edit/', self.admin_site.admin_view(self.edit_story), name='story_edit'),  # New URL for edit
        ]
        return custom_urls + urls

    def preview_story(self, request, story_id):
        if story_id == '0':
            messages.error(request, "Please save the story first to preview it.")
            return redirect('admin:story_story_add')
        story = get_object_or_404(Story, id=story_id)
        if not (story.can_view(request.user) or (story.author == request.user and story.status == 'draft')):
            raise PermissionDenied
        return redirect('story:blog_details', slug=story.slug)
    
    # --- Bulk Action ---
    def submit_for_review(self, request, queryset):
        for story in queryset:
            if story.author == request.user and story.status == 'draft':
                # ✅ Check if story has at least one chapter
                if story.chapters.count() == 0:
                    messages.error(
                        request,
                        f"Cannot submit '{story.title}' for review because it has no chapters."
                    )
                    continue

                story.status = 'review'
                story.save()
                messages.success(request, f"Story '{story.title}' submitted for review.")
            else:
                messages.error(request, f"Cannot submit '{story.title}' for review.")
    submit_for_review.short_description = "Submit selected stories for review"

    # --- Button/Inline View ---
    def submit_for_review_view(self, request, story_id):
        if story_id == '0':
            messages.error(request, "Please save the story first to submit for review.")
            return redirect('admin:story_story_add')

        story = get_object_or_404(Story, id=story_id)

        if story.author != request.user or story.status != 'draft':
            messages.error(request, "You cannot submit this story for review.")
            return redirect('admin:story_story_change', story_id)

        #  Prevent review submission if no chapters
        if story.chapters.count() == 0:
            messages.error(
                request,
                "You must add at least one chapter before submitting this story for review."
            )
            return redirect('admin:story_story_change', story_id)

        if request.method == 'POST' and request.POST.get('action') == 'submit_for_review':
            story.status = 'review'
            story.save()
            messages.success(request, f"Story '{story.title}' submitted for review.")
            return redirect('admin:story_story_changelist')

        return redirect('admin:story_story_change', story_id)

    def delete_view(self, request, story_id):
        if story_id == '0':
            messages.error(request, "Please save the story first to delete it.")
            return redirect('admin:story_story_add')
        story = get_object_or_404(Story, id=story_id)
        if not (story.can_edit(request.user) and story.status == 'draft'):
            messages.error(request, "You cannot delete this story.")
            return redirect('admin:story_story_change', story_id)
        if request.method == 'POST' and request.POST.get('action') == 'delete':
            story.delete()
            messages.success(request, f"Story '{story.title}' deleted successfully.")
            return redirect('admin:story_story_changelist')
        return redirect('admin:story_story_change', story_id)

    def edit_story(self, request, story_id):
        """Custom view to edit an existing story."""
        if story_id == '0':
            messages.error(request, "Please save the story first to edit it.")
            return redirect('admin:story_story_add')
        story = get_object_or_404(Story, id=story_id)
        if not story.can_edit(request.user):
            raise PermissionDenied
        return redirect('admin:story_story_change', story_id)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        story = self.get_object(request, object_id)
        if story and story.can_view(request.user):
            extra_context['show_buttons'] = (
                story.status == 'draft' and 
                story.author == request.user and 
                hasattr(request.user, 'profile') and 
                request.user.profile.is_editor and 
                not request.user.profile.is_chief_editor and 
                not request.user.is_superuser
            )
            extra_context['story_id'] = str(story.id) if story else None
            extra_context['story_slug'] = story.slug if story else None
        return super().change_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_buttons'] = (
            hasattr(request.user, 'profile') and 
            request.user.profile.is_editor and 
            not request.user.profile.is_chief_editor and 
            not request.user.is_superuser
        )
        return super().add_view(request, form_url, extra_context)
    from django.db import transaction




   

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        #  Ensure author is assigned before saving a new story
        if not change or obj.author_id is None:
            obj.author = request.user

        print("Saving story with data:", form.cleaned_data)

        # Step 1: Default status for new stories
        if not change:
            obj.status = 'draft'

        # Step 2: Prevent unauthorized publish/reject
        if (
            'status' in form.changed_data
            and obj.status in ['published', 'rejected']
            and not (
                request.user.is_superuser
                or (hasattr(request.user, 'profile') and request.user.profile.is_chief_editor)
            )
        ):
            obj.status = 'draft'

        # Block submitting or publishing without chapters
        if (
            'status' in form.changed_data
            and obj.status in ['submitted_for_review', 'published']
        ):
            chapter_count = obj.chapters.count()

            if chapter_count == 0:
                messages.error(
                    request,
                    "You must add at least one chapter before submitting ."
                )
                obj.status = 'draft'
                obj.save()
                return redirect('admin:story_story_change', obj.pk)

        # Step 4: Add reviewer info
        if obj.status in ['published', 'rejected']:
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()

        # Step 5: Save normally
        super().save_model(request, obj, form, change)


    @transaction.atomic
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in instances:
            obj.save()
        formset.save_m2m()

        story = form.instance
        chapter_count = story.chapters.count()

        # Detect user role
        user = request.user
        is_chief = hasattr(user, 'profile') and getattr(user.profile, 'is_chief_editor', False)
        is_editor = hasattr(user, 'profile') and getattr(user.profile, 'is_editor', False)

        # ===== Validation Rules =====
        # 1. Editor submitting for review => must have chapters
        if is_editor and story.status == 'review' and chapter_count < 1:
            messages.error(request, "Editors must add at least one chapter before submitting for review.")
            story.status = 'draft'
            story.save()
            return redirect(request.path)

        # 2. Chief editor publishing => must have chapters
        if is_chief and story.status == 'published' and chapter_count < 1:
            messages.error(request, "Chief Editor must add at least one chapter before publishing.")
            story.status = 'draft'
            story.save()
            return redirect(request.path)

        # 3. Otherwise, save normally
        super().save_formset(request, form, formset, change)

        
    # @transaction.atomic  # Atomic transaction covers save_model
    # def save_model(self, request, obj, form, change):
    #     print("Saving story with data:", form.cleaned_data)
    #     if not change:
    #         obj.author = request.user
    #         obj.status = 'draft'
    #     if 'status' in form.changed_data and obj.status in ['published', 'rejected'] and not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_chief_editor)):
    #         obj.status = 'draft'
    #     if obj.status in ['published', 'rejected']:
    #         obj.reviewed_by = request.user
    #         obj.reviewed_at = timezone.now()
    #     super().save_model(request, obj, form, change)

    # Reduce size of image and story_banner fields
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in ('image', 'story_banner'):
            kwargs['widget'] = forms.ClearableFileInput(attrs={'style': 'max-width: 150px; display: inline-block;'})
        return super().formfield_for_dbfield(db_field, request, **kwargs)

@admin.register(StoryChapter)
class StoryChapterAdmin(admin.ModelAdmin):
    list_display = ['title', 'story', 'order', 'image', 'created_at']
    list_filter = ['created_at', 'story']
    search_fields = ['title', 'content', 'story__title']
    list_editable = ['order']
    ordering = ['story', 'order']
    classes = ['collapse', 'wide']  
    
    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }

    def has_change_permission(self, request, obj=None):
        if not obj:
            return True

        #  Chief Editor hamesha edit kar sakta hai
        if request.user.is_superuser or (
            hasattr(request.user, 'profile') and request.user.profile.is_chief_editor
        ):
            return True

        #  Editor sirf tab edit kar sakta hai jab story draft ho
        if hasattr(request.user, 'profile') and request.user.profile.is_editor:
            return obj.story.status == "draft"

        return False

    def has_delete_permission(self, request, obj=None):
        if not obj:
            return True

        if request.user.is_superuser or (
            hasattr(request.user, 'profile') and request.user.profile.is_chief_editor
        ):
            return True

        if hasattr(request.user, 'profile') and request.user.profile.is_editor:
            return obj.story.status == "draft"

        return False

    def has_add_permission(self, request):
        # if user is chief editor always can edit
        if request.user.is_superuser or (
            hasattr(request.user, 'profile') and request.user.profile.is_chief_editor
        ):
            return True

        #  Editor sirf draft wali stories me chapter add kar sakta hai
        if hasattr(request.user, 'profile') and request.user.profile.is_editor:
            story_id = request.GET.get("story")
            if story_id:
                from .models import Story
                try:
                    story = Story.objects.get(pk=story_id)
                    return story.status == "draft"
                except Story.DoesNotExist:
                    return False
        return False


# Admin for StoryLike model
@admin.register(StoryLike)
class StoryLikeAdmin(admin.ModelAdmin):
    list_display = ['story', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['story__title', 'user__username']
    date_hierarchy = 'created_at'

@admin.register(StoryView)
class StoryViewAdmin(admin.ModelAdmin):
    list_display = ('story', 'created_at', 'user', 'ip_address')
    list_filter = ('created_at', 'story')
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return StoryView.objects.all().annotate(
            daily_views=Count('id', filter=Q(created_at__date=models.F('created_at')))
        )

# Admin for StoryTag model
@admin.register(StoryTag)
class StoryTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'stories_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']

    def stories_count(self, obj):
        return obj.stories.count()
    stories_count.short_description = 'Stories Count'

from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.core.exceptions import ValidationError
from .models import Story, StoryChapter


"""==== Story Create Form ==== """
class StoryForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Story
        fields = ['title', 'content', 'image', 'story_banner', 'tags', 'summary']


"""==== Story Chapter Form ==== """
class StoryChapterForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = StoryChapter
        fields = ['title', 'content', 'image', 'video', 'order']


"""==== Custom Formset for Validations ===="""
class ConditionalChapterFormSet(BaseInlineFormSet):
     def clean(self):
        super().clean()
        count = 0
        for form in self.forms:
            if not form.cleaned_data.get("DELETE", False) and form.cleaned_data:
                count += 1
        
        # access parent instance (Story)       
        story = self.instance

        # Check story status only when story already exists
        story_status = getattr(story, "status", None)

        # Logic:
        # - if story is draft => 0 chapter allowed
        # - if story is submitted or published => at least 1 chapter required
        if story_status in ["submitted", "published"] and count < 1:
            raise ValidationError("At least one chapter is required before submitting or publishing this story.")


""" inline forset for story-chapters """ 
StoryChapterFormSet = inlineformset_factory(
    Story,
    StoryChapter,
    form=StoryChapterForm,
    formset=ConditionalChapterFormSet,
    extra=1,
    can_delete=True
)          
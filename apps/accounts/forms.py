from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['user_type', 'bio', 'phone', 'website', 'avatar', 'is_verified', 'specialization']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'phone': forms.TextInput(attrs={'placeholder': 'e.g., +1234567890'}),
            'website': forms.URLInput(attrs={'placeholder': 'e.g., https://example.com'}),
            'avatar': forms.ClearableFileInput(),
            'specialization': forms.TextInput(attrs={'placeholder': 'e.g., Sports Journalism'}),
        }

class CustomUserCreationForm(UserCreationForm):
    user_type = forms.ChoiceField(choices=UserProfile.UserType.choices, required=True)
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False)
    phone = forms.CharField(max_length=20, required=False)
    website = forms.URLField(required=False)
    avatar = forms.ImageField(required=False)
    is_verified = forms.BooleanField(required=False, help_text="Check if the user is a verified editor")
    specialization = forms.CharField(max_length=100, required=False, help_text="Area of expertise (e.g., Sports Journalism)")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'user_type', 'bio', 'phone', 'website', 'avatar', 'is_verified', 'specialization')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Update or create UserProfile (signals will also run)
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.user_type = self.cleaned_data['user_type']
            profile.bio = self.cleaned_data['bio']
            profile.phone = self.cleaned_data['phone']
            profile.website = self.cleaned_data['website']
            profile.avatar = self.cleaned_data['avatar']
            profile.is_verified = self.cleaned_data['is_verified']
            profile.specialization = self.cleaned_data['specialization']
            profile.save()
        return user
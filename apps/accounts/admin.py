"""===== IMPORTS ====="""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


"""===== USER PROFILE INLINE (for User Admin) ====="""
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fk_name = 'user'


"""===== CUSTOM USER ADMIN ====="""
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'get_user_type', 'is_staff', 'is_active'
    )
    list_filter = ('profile__user_type', 'is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')

    def get_user_type(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.get_user_type_display()
        return 'N/A'
    get_user_type.short_description = 'User Type'
    get_user_type.admin_order_field = 'profile__user_type'


"""===== RE-REGISTER USER ADMIN ====="""
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


"""===== USER PROFILE ADMIN ====="""
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'is_verified', 'specialization', 'created_at']
    list_filter = ['user_type', 'is_verified', 'created_at']
    search_fields = ['user__username', 'user__email', 'specialization']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'user_type', 'bio', 'avatar')
        }),
        ('Contact Information', {
            'fields': ('phone', 'website')
        }),
        ('Editor Information', {
            'fields': ('is_verified', 'specialization'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

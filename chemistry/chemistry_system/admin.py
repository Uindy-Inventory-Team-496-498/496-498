from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_approved', 'is_staff')
    list_filter = ('is_approved', 'is_staff')
    actions = ['approve_users']

    def approve_users(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, "Selected users have been approved.")
    approve_users.short_description = "Approve selected users"

admin.site.register(CustomUser, CustomUserAdmin)
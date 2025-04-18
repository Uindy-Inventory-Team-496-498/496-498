from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Register your models here.
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass

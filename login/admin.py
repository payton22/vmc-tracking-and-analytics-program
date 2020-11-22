from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser()
    ordering = ('email',)


# Register your models here.
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.unregister(Group)

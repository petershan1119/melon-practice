from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {'fields': (
            'username',
            'password',
        )}),
        ('개인정보', {'fields': (
            'first_name',
            'last_name',
            'email',
            'img_profile',
        )}),
        ('권한', {'fields': (
            'is_active',
            'is_staff',
            'is_superuser',
        )}),
        ('중요 일자', {'fields': (
            'last_login',
            'date_joined',
        )}),
    )


admin.site.register(User, UserAdmin)
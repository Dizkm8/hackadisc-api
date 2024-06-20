from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import User
# Register your models here.


class PignusUserAdmin(UserAdmin):
    model = User
    list_display = ['rut', 'user_name', 'role']
    list_filter = ['role']
    fieldsets = [
        (None, {'fields': ('rut', 'password')}),
        ('Personal info', {'fields': ['user_name']}),
        ('Permissions', {'fields': ['role']}),
    ]
    add_fieldsets = [
        (None, {
            'classes': ['wide'],
            'fields': ['rut', 'user_name', 'password1', 'password2']}
         ),
    ]
    search_fields = ['rut']
    ordering = ['rut']
    filter_horizontal = []


admin.site.register(User, PignusUserAdmin)
admin.site.unregister(Group)
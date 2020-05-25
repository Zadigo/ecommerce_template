from django.contrib import admin
from django.contrib.auth.models import Group

from accounts.models import MyUser, MyUserProfile, SubscribedUser


@admin.register(MyUser)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'surname', 'is_active', 'admin']
    list_filter  = ['is_active']
    readonly_fields = ['password']
    search_fields = ['name', 'surname', 'email']
    fieldsets = [
        ['Details', {'fields': ['name', 'surname']}],
        ['Credentials', {'fields': ['email', 'password']}],
        ['Permissions', {'fields': ['is_active', 'admin']}]
    ]
    ordering = ['email']

@admin.register(MyUserProfile)
class MyUserProfileAdmin(admin.ModelAdmin):
    actions      = ('activate_account', 'deactivate_account',)
    list_display = ('myuser', 'telephone',)
    search_fields = ['myuser__name', 'myuser__surname', 'myuser__email']

    def activate_account(self, request, queryset):
        queryset.update(actif=True)

    def deactivate_account(self, request, queryset):
        queryset.update(actif=False)

@admin.register(SubscribedUser)
class SubscribedUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'created_on']
    date_hierarchy = 'created_on'
    list_filter = ['created_on']

admin.site.unregister(Group)

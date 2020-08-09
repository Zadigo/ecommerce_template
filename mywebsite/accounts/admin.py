from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth.models import Group, Permission, User

from accounts import forms
from accounts.models import MyUser, MyUserProfile, SubscribedUser


class MyUserAdmin(auth_admin.UserAdmin):
    form = forms.MyUserChangeForm
    add_form = forms.MyUserCreationForm
    model = MyUser

    list_display = ['email', 'name', 'surname', 'is_active', 'is_admin']
    list_filter = ()
    filter_horizontal = ()
    ordering = ['email']
    search_fields = ['name', 'surname', 'email']
    fieldsets = [
        ['Details', {'fields': ['name', 'surname']}],
        ['Credentials', {'fields': ['email', 'password']}],
        ['Permissions', {'fields': ['is_admin', 'is_staff', 'is_active', 'product_manager']}]
    ]
    add_fieldsets = [
        [None, {
                'classes': ['wide'],
                'fields': ['email', 'password1', 'password2', 'is_admin', 'is_staff', 'is_active', 'product_manager']
            }
        ],
    ]
    ordering = ['email']


admin.site.register(MyUser, MyUserAdmin)

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
# admin.site.register(Permission)

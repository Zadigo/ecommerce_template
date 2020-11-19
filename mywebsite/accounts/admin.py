from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth.models import Group

from accounts import forms
from accounts import models

from django.contrib.admin.sites import AdminSite
from django.http import HttpResponseRedirect
from django.views.decorators.cache import never_cache
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import reverse
from django.utils.translation import gettext_lazy as _



from django.contrib.auth import authenticate
from django.contrib.admin.forms import AdminAuthenticationForm

# class CustomAdminAuthenticationForm(AdminAuthenticationForm):
#     def clean(self):
#         email = self.cleaned_data.get('email')
#         password = self.cleaned_data.get('password')

#         if email is not None and password:
#             self.user_cache = authenticate(self.request, email=email, password=password)
#             if self.user_cache is None:
#                 raise self.get_invalid_login_error()
#             else:
#                 self.confirm_login_allowed(self.user_cache)
#         return self.cleaned_data

# class CustomAdminSite(AdminSite):
#     @never_cache
#     def login(self, request, extra_context=None):
#         if request.method == 'GET' and self.has_permission(request):
#             index_path = reverse('admin:index', current_app=self.name)
#             return HttpResponseRedirect(index_path)

#         from django.contrib.auth.views import LoginView

#         context = {
#             **self.each_context(request),
#             'title': _("Log in"),
#             'app_path': request.get_full_path(),
#             'username': request.uer.get_username()
#         }

#         if (REDIRECT_FIELD_NAME not in request.GET and
#                 REDIRECT_FIELD_NAME not in request.POST):
#             context[REDIRECT_FIELD_NAME] = reverse('admin:index', current_app=self.name)
#         context.update(extra_context or {})

#         defaults = {
#             'extra_context': context,
#             'authentication_form': self.login_form or AdminAuthenticationForm,
#             'template_name': self.login_template or 'admin/login.html',
#         }
#         request.current_app = self.name
#         return LoginView.as_view(**defaults)(request)
        

@admin.register(models.MyUser)
class MyUserAdmin(auth_admin.UserAdmin):
    form = forms.MyUserChangeForm
    add_form = forms.MyUserCreationForm
    model = models.MyUser

    list_display = ['email', 'firstname', 'lastname', 'is_active', 'is_admin']
    list_filter = ()
    filter_horizontal = ()
    ordering = ['email']
    search_fields = ['firstname', 'lastname', 'email']
    fieldsets = [
        ['Details', {'fields': ['firstname', 'lastname']}],
        ['Credentials', {'fields': ['email', 'password']}],
        ['Permissions', {'fields': ['is_admin', 'is_staff', 'is_active']}]
    ]
    add_fieldsets = [
        [None, {
                'classes': ['wide'],
                'fields': ['email', 'password1', 'password2', 'is_admin', 'is_staff', 'is_active']
            }
        ],
    ]
    ordering = ['email']


@admin.register(models.MyUserProfile)
class MyUserProfileAdmin(admin.ModelAdmin):
    actions      = ('activate_account', 'deactivate_account',)
    list_display = ('myuser', 'telephone',)
    search_fields = ['myuser__firstname', 'myuser__lastname', 'myuser__email']

    def activate_account(self, request, queryset):
        queryset.update(actif=True)

    def deactivate_account(self, request, queryset):
        queryset.update(actif=False)

admin.site.unregister(Group)

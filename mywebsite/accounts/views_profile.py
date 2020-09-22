import datetime
import re

import stripe
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView, View

from accounts import forms
from accounts.models import MyUser, MyUserProfile


class IndexView(TemplateView):
    template_name = 'pages/profile/index.html'


class InformationView(LoginRequiredMixin, View):
    forms = {
        'form1': forms.BaseProfileForm,
        'form2': forms.AddressProfileForm
    }

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(MyUser, id=request.user.id)
        profile = user.myuserprofile

        context = {
            'form1': self.forms['form1'](
                initial={
                    'firstname': user.firstname,
                    'lastname': user.lastname,
                    'email': user.email
                }
            ),
            'form2': self.forms['form2'](
                initial={
                    'address': profile.address,
                    'city': profile.city,
                    'zip_code': profile.zip_code
                }
            )
        }
        return render(request, 'pages/profile/information.html', context)

    def post(self, request, **kwargs):
        user = MyUser.objects.get(id=request.user.id)
        user_profile = user.myuserprofile

        position = int(request.POST.get('position'))

        if position == 0:
            form = self.forms['form1'](request.POST, instance=user)

        if position == 1:
            form = self.forms['form2'](request.POST, instance=user_profile)

        if not form:
            messages.error(request, _("An error occured - FOR-NR"),
                           extra_tags='alert-danger')
            # return JsonResponse(data={'state': False})
            return redirect(reverse('accounts:profile:home'))
        else:
            if form.is_valid():
                form.save()

        # return JsonResponse(data={'state': True})
        messages.success(request, _("Informations modifiées"), extra_tags='alert-success')
        return redirect(reverse('accounts:profile:home'))


class ProfileDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        current_user = self.request.user

        try:
            # Query the social_auth database and
            # get a set of connected accounts
            user = self.request.user.social_auth.get(uid=current_user.email)
            if user:
                context = {
                    'provider': user.provider
                }
        except:
            context = {}

        return render(request, 'pages/profile/data.html', context)


class ProfileDeleteView(LoginRequiredMixin, View):
    """Help the user delete his account
    """

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(MyUser, id=request.user.id)
        user.delete()
        return redirect('/')


class PaymentMethodsView(LoginRequiredMixin, View):
    """Allows the customer to update his/her payment method"""

    def get(self, request, *args, **kwargs):
        myprofile = MyUserProfile.objects.get(myuser=request.user.id)
        try:
            details = stripe.Customer.retrieve(myprofile.stripe_id)
        except Exception:
            details = {}
            messages.error(request, _("Une erreur s'est produite - STR-PA"), extra_tags='alert-danger')
        return render(request, 'pages/profile/payments.html', {'details': details})


class ChangePasswordView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {
            'form': forms.CustomChangePasswordForm(request.user),
        }
        return render(request, 'pages/profile/change_password.html', context)

    def post(self, request, **kwargs):
        form = forms.CustomChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
        return redirect('/profile/')


class ContactPreferencesView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/profile/contact.html'

    def post(self, request, **kwargs):
        pass

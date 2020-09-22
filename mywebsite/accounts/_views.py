"""
This module utilizes the classic View class
for signup and login as opposed to the view
module that uses FormView
"""


import datetime
import re

from django.contrib import auth, messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages import add_message, error, success
from django.core.mail import BadHeaderError, send_mail
from django.http.response import (
    Http404, HttpResponse, HttpResponseForbidden, HttpResponseRedirect)
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.generic import FormView, RedirectView, View

from accounts import forms, models

MYUSER = auth.get_user_model()

class SignupView(View):
    """View that helps the user create a new account"""
    def get(self, request, *args, **kwargs):
        context = {'consent': True, 'form': forms.UserSignupForm}
        return render(request, 'pages/registration/signup.html', context)

    def post(self, request, **kwargs):
        email = request.POST['email']

        user_exists = MYUSER.objects.filter(email__iexact=email).exists()
        if user_exists:
            return redirect(reverse('login'))

        else:
            form = forms.UserSignupForm(data=request.POST)
            if form.is_valid():
                user = form.save()
                if user:
                    email = form.cleaned_data.get('email')
                    password = form.cleaned_data.get('password2')
                    auth.login(request, auth.authenticate(request, email=email, password=password))
                    return redirect(request.GET.get('next') or reverse('profile'))
            else:
                return render(request, 'pages/registration/signup.html', {'form': form})


class LoginView(View):
    """View that lets the user login to his account"""
    def get(self, request, *args, **kwargs):
        return render(request, 'pages/registration/login.html', context={'form': forms.UserLoginForm})

    def post(self, request, **kwargs):
        # HACK: Even with the email field,
        # the latter is referenced as
        # 'username'
        email = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(request, email=email, password=password)
        if user:
            auth.login(request, user)
            return redirect(request.GET.get('next') or 'home')
        else:
            messages.error(request, "Nous n'avons pas pu trouver votre compte")
            return redirect('accounts:login')

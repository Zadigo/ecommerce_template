import datetime
import re

from django.contrib import auth, messages
from django.contrib.auth.forms import (PasswordChangeForm, PasswordResetForm,
                                       SetPasswordForm)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages import add_message, error, success
from django.core.mail import BadHeaderError, send_mail
from django.http.response import HttpResponseForbidden
from django.shortcuts import (Http404, HttpResponse, get_object_or_404,
                              redirect, render, reverse)
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.views.generic import View

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


class LogoutView(View):
    """Logs out the user from their account"""
    def get(self, request, *args, **kwargs):
        auth.logout(request)
        return redirect('home')


class ForgotPasswordView(View):
    """
    A single field form where the user can ask for
    a password reset
    """
    def get(self, request, *args, **kwargs):
        context = {'form': forms.CustomPassowordResetForm}
        return render(request, 'pages/registration/forgot_password.html', context)

    def post(self, request, **kwargs):
        form = forms.CustomPassowordResetForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']

            user = MYUSER.objects.filter(email__iexact=email)
            if user.exists():
                # NOTE: Change to append a token to the url
                # which will help iD the user in the confirm view
                form.save(request, 'contact.mywebsite@gmail.com')
            else:
                messages.error(request, "Nous n'avons pas pu vous trouvez votre addresse mail", extra_tags='alert-danger')
                context = {'form': forms.CustomPassowordResetForm}
                return render(request, 'pages/registration/forgot_password.html', context=context)

        return redirect('accounts:login')


class UnauthenticatedPasswordResetView(View):
    """
    Helps a non authenticated user reset his password
    """
    def get(self, request, *args, **kwargs):
        # user_token = request.GET.get('user_token')
        # if not user_token:
        #     return HttpResponseForbidden(reason='Missing argument')
        
        context = {
            'form': forms.CustomSetPasswordForm(MYUSER.objects.get(id=1)),
        }
        return render(request, 'pages/registration/forgot_password_confirm.html', context)

    def post(self, request, **kwargs):
        # user_token = request.GET.get('user_token')
        # user = get_object_or_404(MYUSER, id=user_token)
        form = forms.CustomSetPasswordForm(user)
        if form.is_valid():
            form.save()
        auth.login(request, user)
        return redirect('profile')

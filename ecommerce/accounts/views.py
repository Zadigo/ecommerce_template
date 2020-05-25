import datetime
import re

from django.contrib import messages
from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
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
from django.views.generic import View

from accounts.forms import UserLoginForm, UserSignupForm
from accounts.models import MyUser




# #####################
#  REGISTRATION VIEWS
# #####################

class SignupView(View):
    """View that helps the user create a new account"""
    def get(self, request, *args, **kwargs):
        context = {'consent': True, 'form': UserSignupForm}
        return render(request, 'pages/registration/signup.html', context)

    def post(self, request, **kwargs):
        # name = request.POST['name']
        # surname = request.POST['surname']
        email = request.POST['email']
        # password = request.POST['password']

        user_exists = MyUser.objects.filter(email__iexact=email).exists()
        if user_exists:
            return redirect(reverse('login'))
            
        else:
            # user = MyUser.objects.create_user(email, name=name, surname=surname, password=password)
            # if user:
            #     login(request, authenticate(request, email=email, password=password))
            #     return redirect(request.GET.get('next') or reverse('profile'))

            form = UserSignupForm(data=request.POST)
            if form.is_valid():
                user = form.save()
                if user:
                    email = form.cleaned_data.get('email')
                    password = form.cleaned_data.get('password2')
                    login(request, authenticate(request, email=email, password=password))
                    return redirect(request.GET.get('next') or reverse('profile'))
            else:
                return render(request, 'pages/registration/signup.html', {'form': form})

class LoginView(View):
    """View that lets the user login to his account"""
    def get(self, request, *args, **kwargs):
        return render(request, 'pages/registration/login.html', context={'form': UserLoginForm})

    def post(self, request, **kwargs):
        # HACK: Even with the email field,
        # the latter is referenced as
        # 'username'
        email = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get('next') or 'home')
        else:
            error(request, 'We could not find your account')
            return redirect('login')

class LogoutView(View):
    """Logs out the user from their account"""
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('home')

class ForgotPasswordView(View):
    """THelps a non authenticated user reset his password"""
    def get(self, request, *args, **kwargs):
        context = {'form': PasswordResetForm}
        return render(request, 'pages/registration/forgot_password.html', context)

    def post(self, request, **kwargs):
        form = PasswordResetForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            user = MyUser.objects.filter(email__iexact=email)
            if user.exists():
                # NOTE: Change to append a token to the url
                # which will help iD the user in the confirm view
                form.save(from_email='pendenquejohn@gmail.com', request=request)

            else:
                form.errors['email'] = _("Nous n'avons pas pu vous trouvez votre addresse mail")
                context = {
                    'form': PasswordResetForm,
                    'form_button_registration': _('Nouveau mot de passe')
                }
                return render(request, 'pages/registration/forgot_password.html', context=context)

        return redirect('login')

class UnauthenticatedChangePasswordView(View):
    """Shows the user a form that helps reset his
    password once he has initiated the process"""
    def get(self, request, *args, **kwargs):
        user_token = request.GET.get('user_token')
        if not user_token:
            return HttpResponseForbidden(reason='Missing argument')
        
        context = {
            'form': SetPasswordForm(MyUser.objects.get(id=1)),
            'form_button_registration': _('Modifier')
        }
        return render(request, 'pages/registration/forgot_password_confirm.html', context)

    def post(self, request, **kwargs):
        user_token = request.GET.get('user_token')
        user = get_object_or_404(MyUser, id=user_token)
        form = SetPasswordForm(user)
        if form.is_valid():
            form.save()
        login(request, user)
        return redirect('/profile/')

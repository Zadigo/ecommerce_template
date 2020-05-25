from django import forms
from django.contrib.admin import AdminSite
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import (AuthenticationForm,
                                       ReadOnlyPasswordHashField,
                                       UserCreationForm, UserChangeForm)
from django.forms import CharField, EmailField
from django.forms.widgets import EmailInput, PasswordInput, Select, TextInput
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from accounts.models import MyUser, MyUserProfile


class CustomUserCreationForm(UserCreationForm):
    email     = EmailField(required=True)
    password1 = CharField(label=_('Password'), widget=PasswordInput)
    password2 = CharField(label=_('Password confirmation'), widget=PasswordInput)

    class Meta:
        model = MyUser
        fields = ['surname', 'name', 'email', 'password',\
                    'admin', 'staff']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Passwords don't match"))

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()

        return user
        
class CustomUserChangeForm(UserChangeForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = MyUser
        fields = ['email', 'password']

    def clean_password(self):
        return self.initial["password"]

class UserLoginForm(AuthenticationForm):
    username    = EmailField(widget=EmailInput(attrs={'placeholder': _('Email professionnel')}))
    password    = CharField(strip=False, widget=PasswordInput(attrs={'placeholder': _('Mot de passe')}))
    
    def clean(self):
        email    = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email is None and password:
            raise forms.ValidationError(_("Veuillez entrer un email ainsi qu'un mot de passe"))    

        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)

            if self.user_cache:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def authenticate(self):
        pass

class UserSignupForm(UserCreationForm):
    class Meta:
        model = MyUser
        fields = ['name', 'surname', 'email']
        widgets = {
            'surname': TextInput(attrs={'placeholder': 'Nom'}),
            'name': TextInput(attrs={'placeholder': 'Prénom'}),
            'email': EmailInput(attrs={'placeholder': 'Email'}),
        }

    def clean(self):
        password1 = self.cleaned_data.get('password1')

        if password1 is None:
            raise forms.ValidationError('Veuillez entrer un mot de passe')

        if len(password1) < 10:
            raise forms.ValidationError('Votre mot de passe doit comporter au moins 10 charactères')

        return self.cleaned_data

# class UserSignupForm(forms.Form):
#     name         = CharField(widget=TextInput(attrs={'placeholder': _('Joe')}))
#     surname      = CharField(widget=TextInput(attrs={'placeholder': _('Doe')}))
#     email       = EmailField(widget=EmailInput(attrs={'placeholder': _('johndoe@gmail.com')}))
#     password    = CharField(widget=PasswordInput(attrs={'placeholder': _('Mot de passe')}))





# #####################
#   Profile forms
# #####################

class BaseProfileForm(forms.ModelForm):
    class Meta:
        model   = MyUser
        fields  = ['name', 'surname']
        widgets = {
            'name': TextInput(attrs={'placeholder': 'John'}),
            'surname': TextInput(attrs={'placeholder': 'Doe'}),
        }

class AddressProfileForm(forms.ModelForm):
    class Meta:
        model   = MyUserProfile
        fields  = ['address', 'city', 'zip_code']
        widgets = {
            'address': TextInput(attrs={'placeholder': '173 rue de Rivoli'}),
            'city': TextInput(attrs={'placeholder': 'Paris'}),
            'zip_code': TextInput(attrs={'placeholder': '59120'})
        }

class AnonymousUserForm(forms.Form):
    address = CharField(max_length='100', required=True, widget=TextInput(attrs={'autocomplete': 'address-line-1', 'placeholder': '34 rue de Paris'}))
    city = CharField(max_length='45', required=True, widget=TextInput(attrs={'autocomplete': 'city', 'placeholder': 'Lille'}))
    zip_code = CharField(max_length='100', required=True, widget=TextInput(attrs={'autocomplete': 'zip-code', 'placeholder': '59000'}))
    country = CharField(max_length='45', widget=Select(attrs={'autocomplete': 'country', 'placeholder': 'France'}, choices=(('france', 'France'),)))

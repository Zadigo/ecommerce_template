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


class MyUserCreationForm(forms.ModelForm):
    password1 = CharField(label=_('Password'), widget=PasswordInput)
    password2 = CharField(label=_('Password confirmation'), widget=PasswordInput)

    class Meta:
        model = MyUser
        fields = ['email', 'is_staff', 'product_manager']

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
        
class MyUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = MyUser
        fields = ['email', 'password']

    def clean_password(self):
        return self.initial['password']

class UserLoginForm(AuthenticationForm):
    username    = EmailField(widget=EmailInput(attrs={'class': 'form-input', 'placeholder': _('Email')}))
    password    = CharField(strip=False, widget=PasswordInput(attrs={'class': 'from-input', 'placeholder': _('Mot de passe')}))
    
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

class UserSignupForm(UserCreationForm):
    class Meta:
        model = MyUser
        fields = ['name', 'surname', 'email']
        widgets = {
            'surname': TextInput(attrs={'class': 'form-input', 'placeholder': 'Nom'}),
            'name': TextInput(attrs={'class': 'form-input', 'placeholder': 'Prénom'}),
            'email': EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'}),
        }

    def clean(self):
        password1 = self.cleaned_data.get('password1')

        if password1 is None:
            raise forms.ValidationError('Veuillez entrer un mot de passe')

        if len(password1) < 10:
            raise forms.ValidationError('Votre mot de passe doit comporter au moins 10 charactères')

        return self.cleaned_data




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

class DashboardLoginForm(forms.Form):
    email = forms.CharField(widget=EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'}))
    authentication_token = forms.CharField(required=False, max_length=70, widget=PasswordInput(attrs={'class': 'form-control', 'placeholder': "Token d'authentication"}))

class DashboardSignupForm(forms.Form):
    nom   = forms.CharField(widget=TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}))
    prenom   = forms.CharField(widget=TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}))
    email = forms.CharField(widget=EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    token   = forms.CharField(widget=TextInput(attrs={'class': 'form-control', 'placeholder': 'Token'}))

    def clean(self):
        token = self.cleaned_data['token']
        password = self.cleaned_data['password']
        if len(password) < 10:
            raise forms.ValidationError('Le mot de passe doit être supérieur à 10 charactères')
        if token != 'gloria':
            raise forms.ValidationError("Le token n'est pas  valide")
        return dict(name=self.cleaned_data['nom'], surname=self.cleaned_data['prenom'], \
                email=self.cleaned_data['email'], password=self.cleaned_data['password'])
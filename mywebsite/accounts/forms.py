from django import forms
from django.contrib.admin import AdminSite
from django.contrib.auth import authenticate
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import get_user_model, password_validation
from django.forms import fields, widgets
from django.contrib.auth.tokens import default_token_generator
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from accounts.models import MyUserProfile


MYUSER = get_user_model()

class MyUserCreationForm(forms.ModelForm):
    password1 = fields.CharField(label=_('Password'), widget=widgets.PasswordInput)
    password2 = fields.CharField(label=_('Password confirmation'), widget=widgets.PasswordInput)

    class Meta:
        model = MYUSER
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
    password = auth_forms.ReadOnlyPasswordHashField()

    class Meta:
        model = MYUSER
        fields = ['email', 'password']

    def clean_password(self):
        return self.initial['password']


class UserLoginForm(auth_forms.AuthenticationForm):
    username    = fields.EmailField(
        widget=widgets.EmailInput(
            attrs={'class': 'form-control', 'placeholder': _('Email')}
        )
    )
    password    = fields.CharField(
        strip=False, 
        widget=widgets.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': _('Mot de passe'), 'autocomplete': 'current-password'}
        )
    )
    
    def clean(self):
        email    = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email is None and password:
            raise forms.ValidationError(_("Veuillez entrer un email ainsi qu'un mot de passe"))    

        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)

            if self.user_cache:
                self.confirm_login_allowed(self.user_cache)
            else:
                raise forms.ValidationError("Vous n'êtes pas autorisé à vous connecté")

        return self.cleaned_data


class UserSignupForm(auth_forms.UserCreationForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password', 'placeholder': 'Mot de passe'}),
        strip=False,
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password', 'placeholder': 'Confirmation du mot de passe'}),
        strip=False
    )

    class Meta:
        model = MYUSER
        fields = ['name', 'surname', 'email']
        widgets = {
            'surname': widgets.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'name': widgets.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'email': widgets.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }

    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if not password1:
            raise forms.ValidationError('Veuillez entrer un mot de passe')
        
        if password1 != password2:
            raise forms.ValidationError('Les mots de passe ne correspondent pas')

        if len(password1) < 10:
            raise forms.ValidationError('Votre mot de passe doit comporter au moins 10 charactères')

        return self.cleaned_data


class CustomPassowordResetForm(auth_forms.PasswordResetForm):
    email = forms.EmailField(
        label=_('Email'),
        max_length=254,
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'autocomplete': 'email', 'placeholder': 'Email'}
        )
    )

    def save(self, request, from_email):
        super().save(
            from_email=from_email,
            subject_template_name='components/emails/password_reset_subject.txt',
            email_template_name='components/emails/password_reset_email.html',
            request=request
        )


class CustomSetPasswordForm(auth_forms.SetPasswordForm):
    new_password1 = forms.CharField(
        label=_('Nouveau mot de passe'),
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Nouveau mot de passe','autocomplete': 'off'}
        ),
        strip=False
    )
    new_password2 = forms.CharField(
        label=_('Nouveau mot de passe confirmation'),
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Nouveau mot de passe confirmation', 'autocomplete': 'off'}
        ),
        strip=False,
    )



# #####################
#   Profile forms
# #####################

class BaseProfileForm(forms.ModelForm):
    class Meta:
        model   = MYUSER
        fields  = ['name', 'surname']
        widgets = {
            'name': widgets.TextInput(attrs={'placeholder': 'John'}),
            'surname': widgets.TextInput(attrs={'placeholder': 'Doe'}),
        }


class AddressProfileForm(forms.ModelForm):
    class Meta:
        model   = MyUserProfile
        fields  = ['address', 'city', 'zip_code']
        widgets = {
            'address': widgets.TextInput(attrs={'placeholder': '173 rue de Rivoli'}),
            'city': widgets.TextInput(attrs={'placeholder': 'Paris'}),
            'zip_code': widgets.TextInput(attrs={'placeholder': '59120'})
        }


class AnonymousUserForm(forms.Form):
    address = fields.CharField(max_length='100', required=True, widget=widgets.TextInput(attrs={'autocomplete': 'address-line-1', 'placeholder': '34 rue de Paris'}))
    city = fields.CharField(max_length='45', required=True, widget=widgets.TextInput(attrs={'autocomplete': 'city', 'placeholder': 'Lille'}))
    zip_code = fields.CharField(max_length='100', required=True, widget=widgets.TextInput(attrs={'autocomplete': 'zip-code', 'placeholder': '59000'}))
    country = fields.CharField(max_length='45', widget=widgets.Select(attrs={'autocomplete': 'country', 'placeholder': 'France'}, choices=(('france', 'France'),)))

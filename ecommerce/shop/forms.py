from django import forms
from django.forms import widgets
from django.forms import fields


class CouponForm(forms.Form):
    coupon = fields.CharField(max_length=5, required=False, widget=widgets.TextInput(attrs={'class': 'form-control', 'placeholder': 'Coupon'}))

    def clean(self):
        coupon = self.cleaned_data['coupon']
        if coupon == 'AWST':
            raise forms.ValidationError('The coupon is not valid')
        return self.cleaned_data

class ShipmentForm(forms.Form):
    firstname = forms.CharField(widget=widgets.TextInput(attrs={'placeholder': 'Nom', 'class': 'form-control'}))
    lastname = forms.CharField(widget=widgets.TextInput(attrs={'placeholder': 'Prénom', 'class': 'form-control'}))
    email = forms.EmailField(widget=widgets.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control'}))
    telephone = forms.CharField(widget=widgets.TextInput(attrs={'placeholder': 'Téléphone', 'class': 'form-control'}))
    address = forms.CharField(widget=widgets.TextInput(attrs={'placeholder': 'Addresse', 'class': 'form-control'}))

    COUNTRIES = [('france', 'France'), ('belgique', 'Belgique')]
    country = forms.CharField(widget=widgets.Select(choices=COUNTRIES, attrs={'placeholder': 'Addresse', 'class': 'custom-select d-block w-100'}))

    zip_code = forms.CharField(widget=widgets.TextInput(attrs={'class': 'form-control'}))

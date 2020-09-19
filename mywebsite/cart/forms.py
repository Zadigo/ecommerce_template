from django import forms
from django.forms import widgets
from django.forms import fields
from cart import validators, choices

class CouponForm(forms.Form):
    coupon = fields.CharField(max_length=5, widget=widgets.TextInput(attrs={'class': 'form-control', 'placeholder': 'Coupon'}))

    def clean(self):
        coupon = self.cleaned_data['coupon']
        if coupon == 'AWST':
            raise forms.ValidationError("Le code n'est pas valide")
        return self.cleaned_data

class ShipmentForm(forms.Form):
    first_name = forms.CharField(widget=widgets.TextInput(attrs={'name': 'firstname'}))
    last_name   = forms.CharField(widget=widgets.TextInput(attrs={'name': 'lastname'}))
    
    email   = forms.EmailField(widget=widgets.EmailInput())

    telephone = forms.CharField(widget=widgets.TextInput())

    address   = forms.CharField()
    country     = forms.CharField(widget=widgets.Select(choices=choices.Countries.choices))
    city        = forms.CharField(widget=widgets.Select(choices=choices.Cities.choices))
    zip_code    = forms.CharField(validators=[validators.zip_code_validator])

    billing_equals_shipping = forms.BooleanField(required=False, initial=False)
    save_for_next_time      = forms.BooleanField(required=False, initial=False)

    def clean(self):
        cleaned_data = super().cleaned_data
        return cleaned_data

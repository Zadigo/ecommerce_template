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

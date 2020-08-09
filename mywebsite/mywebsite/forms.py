from django import forms
from django.forms import fields, widgets

from shop import models

ATTRS = {'class': 'form-control'}

class ContactForm(forms.Form):
    email = fields.EmailField(widget=widgets.EmailInput(attrs=ATTRS))
    conditions = fields.BooleanField(widget=widgets.CheckboxInput(attrs=ATTRS.update({'class': ''})))
    message = fields.CharField(widget=widgets.Textarea(attrs=ATTRS))

    def clean_message(self):
        message = self.cleaned_data['message']
        if len(message) > 300:
            raise forms.ValidationError("Le messsage est trop long")
        super().clean()

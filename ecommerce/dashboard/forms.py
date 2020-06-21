import datetime

from django import forms
from django.forms import fields, widgets

from dashboard import widgets as custom_widgets
from shop import models, utilities

from django.contrib.auth import get_user_model
from accounts.utils import get_user_profile_model



class ProductForm(forms.ModelForm):
    class Meta:
        model = models.Product
        localized_fields = ('price_valid_until',)
        fields = ['name', 'description', 'gender', 'price_ht', 'discount_pct', 'price_valid_until', \
                        'collection', 'clothe_size', 'reference', 'sku', 'in_stock', 'active', 'our_favorite', 'discounted', 'google_category']
        widgets = {
            'name': widgets.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du produit'}),
            'description': forms.widgets.Textarea(attrs={'class': 'form-control'}),
            'gender': widgets.Select(attrs={'class': 'form-control'}),

            'sku': widgets.TextInput(attrs={'class': 'form-control', 'placeholder': 'SKU'}),
            'reference': widgets.TextInput(attrs={'class': 'form-control', 'placeholder': 'Référence'}),
            
            'price_ht': widgets.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Prix Hors Taxe', 'min': '0'}),
            'price_valid_until': custom_widgets.DateInput(),
            'discount_pct': widgets.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nombre en %', 'min': '0', 'value': '0'}),
            
            'clothe_size': widgets.SelectMultiple(attrs={'class': 'form-control'}),
            'collection': widgets.Select(attrs={'class': 'form-control'}),
            'google_category': widgets.Select(attrs={'class': 'form-control'}),

            'in_stock': widgets.CheckboxInput(attrs={'class': 'custom-control-input', 'id': 'in_stock'}),
            'our_favorite': widgets.CheckboxInput(attrs={'class': 'custom-control-input'}),
            'discounted': custom_widgets.CheckBoxInput(),
            'active': widgets.CheckboxInput(attrs={'class': 'custom-control-input', 'id': 'active'}),
        }

class DiscountForm(forms.ModelForm):
    class Meta:
        model = models.Discount
        fields = ['code', 'value_type', 'value', 'collection', 'on_entire_order',\
         'minimum_purchase', 'minimum_quantity', 'usage_limit', 'start_date', 'end_date']

        widgets = {
            'code': custom_widgets.TextInput(attrs={'placeholder': 'Code'}),
            'value_type': widgets.Select(attrs={'class': 'form-control'}),

            'value': custom_widgets.NumberInput(attrs={'v-model': "fieldsdata['value']"}),
            'collection': widgets.Select(attrs={'class': 'form-control'}),

            'on_entire_order': widgets.CheckboxInput(),
            
            'minimum_purchase': custom_widgets.NumberInput(),
            'minimum_quantity': custom_widgets.NumberInput(),

            'usage_limit': custom_widgets.NumberInput(),

            'start_date': custom_widgets.DateInput(),
            'end_date': custom_widgets.DateInput(),
        }

class CollectionForm(forms.ModelForm):
    class Meta:
        model = models.Collection
        fields = ['name', 'presentation_text']

        widgets = {
            'name': custom_widgets.TextInput(attrs={'placeholder': 'Nom de la collection'}),
            'presentation_text': forms.widgets.Textarea(attrs={'class': 'form-control'}),
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['name', 'surname', 'email']

        widgets = {
            'name': custom_widgets.TextInput(attrs={'placeholder': 'Nom'}),
        }

class ImageForm(forms.ModelForm): 
    class Meta:
        model = models.Image
        fields = ['name', 'url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'url': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Url'})
        }






# class TestForm(forms.Form):
#     google = forms.CharField(widget=custom_widgets.TextInput())
#     apple = forms.CharField(widget=custom_widgets.CheckBoxInput())

# class ImageAssociationForm(forms.Form):
#     products = forms.CharField(widget=forms.Select(attrs={'class': 'form-control'}, \
#             choices=[[product[0], product[0]] for product in models.Product.objects.values_list('name')]))

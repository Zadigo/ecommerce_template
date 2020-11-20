import datetime
import re
from itertools import filterfalse

from django import forms
from django.contrib.auth import get_user_model
from django.forms import widgets
from django.utils.translation import gettext_lazy as _

from cart import models as cart_models
from dashboard import widgets as custom_widgets
from dashboard.mixins import FormMixin
from discounts import models as discount_models
from shop import models 


class ProductForm(forms.ModelForm):
    class Meta:
        model = models.Product
        localized_fields = ('price_valid_until',)
        exclude = ['images', 'variant', 'slug', 'last_modified', 'created_on']
        widgets = {
            'name': custom_widgets.TextInput(attrs={'placeholder': 'Nom du produit'}),
            'description': forms.widgets.Textarea(attrs={'class': 'form-control'}),
            'gender': widgets.Select(attrs={'class': 'form-control'}),

            'sku': custom_widgets.TextInput(attrs={'placeholder': 'SKU'}),
            'reference': custom_widgets.TextInput(attrs={'placeholder': 'Référence'}),
            
            'price_pre_tax': custom_widgets.NumberInput(attrs={'placeholder': 'Prix Hors Taxe', 'min': '0', 'step': 'any'}),
            'price_valid_until': custom_widgets.DateInput(),
            'discount_pct': custom_widgets.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nombre en %', 'min': '5'}),
            'quantity': custom_widgets.NumberInput(attrs={'class': 'form-control', 'step': '5', 'min': '0'}),
            
            'collection': widgets.Select(attrs={'class': 'form-control'}),
            'google_category': widgets.Select(attrs={'class': 'form-control'}),

            'in_stock': widgets.CheckboxInput(attrs={'class': 'custom-control-input'}),
            'our_favorite': widgets.CheckboxInput(attrs={'class': 'custom-control-input'}),
            'discounted': widgets.CheckboxInput(attrs={'class': 'custom-control-input'}),
            'active': widgets.CheckboxInput(attrs={'class': 'custom-control-input'}),
            'private': widgets.CheckboxInput(attrs={'class': 'custom-control-input'}),

            'to_be_published_on': custom_widgets.DateInput()
        }


class UpdateProductForm(FormMixin, ProductForm):
    def save(self):
        """
        This overidding of the save function accounts for permitting
        the user to be able to dynamically add and update sizes using
        our custom Vue JS dynamic input fields on the form.

        Description
        -----------

            - When the user does not add a new input field, no size is created
              since `new-size-name` would not be defined

            - On the other hand, if `new-size-name` is defined, new variants
              fields are created and attached to the product
        """
        product = super().save(commit=False)

        existing_variants = self._update_old_variants(product)
        existing_images = self._update_old_images(product)

        self._create_new_images(product, old_images=existing_images)
        self._create_new_variants(product, old_variants=existing_variants)

        product.save()
        return self.instance
                    
    
class CreateProductForm(FormMixin, ProductForm):
    """
    This overidding of the save function accounts for permitting
    the user to be able to dynamically add and update sizes using
    our custom Vue JS dynamic input fields on the form.

    Description
    -----------

        Creates all the necessary variants once the producth as been
        created
    """

    def save(self):
        product = super().save(commit=False)
        product.save()

        self._create_new_images(product)
        self._create_new_variants(product)

        return self.instance


class DiscountForm(forms.ModelForm):
    class Meta:
        model = discount_models.Discount
        fields = ['code', 'value_type', 'value', 'collection', 'on_entire_order',\
         'minimum_purchase', 'minimum_quantity', 'usage_limit', 'start_date', 'end_date']

        widgets = {
            'code': custom_widgets.TextInput(attrs={'placeholder': 'Code'}),
            'value_type': widgets.Select(attrs={'class': 'form-control'}),

            'value': custom_widgets.NumberInput(),
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
        fields = ['name', 'image', 'presentation_text', 'google_description', 'show_presentation']

        widgets = {
            'name': custom_widgets.TextInput(attrs={'placeholder': 'Nom de la collection'}),
            'presentation_text': forms.widgets.Textarea(attrs={'class': 'form-control'}),
            'image': custom_widgets.CustomFileInput(),
        }

    # def save(self):
    #     collection = super().save(commit=False)
    #     is_automatic_collection = self.data.get('automatic', False)
    #     if is_automatic_collection:
    #         respect_all_conditions = self.data.get('respect_all_conditions', True)
    #         if respect_all_conditions == 'all':
    #             respect_all_conditions = True
    #         else:
    #             respect_all_conditions = False

    #         first_conditions = self.data.getlist('condition1')
    #         second_conditions = self.data.getlist('condition2')
    #         values_to_test = self.data.getlist('value')

    #         items = []
    #         for index, value in enumerate(values_to_test):
    #             if value:
    #                 items.append(
    #                     models.AutomaticCollectionCriteria(
    #                         reference=utilities.create_reference(append_prefix=False),
    #                         condition=choices.SecondConditionsChoices.choices[int(second_conditions[index])],
    #                         value=value
    #                     )
    #                 )

    #         with transaction.atomic():
    #             models.AutomaticCollectionCriteria.objects.bulk_create(items)
    #     collection.save()


class CustomerForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['firstname', 'lastname', 'email']

        widgets = {
            'firstname': custom_widgets.TextInput(attrs={'placeholder': 'Nom'}),
        }


class CustomerOrderForm(forms.ModelForm):
    class Meta:
        model = cart_models.CustomerOrder
        fields = ['accepted', 'shipped', 'refund']

        widgets = {
            'accepted': custom_widgets.CheckBoxInput(),
            'shipped': custom_widgets.CheckBoxInput(),
            'refund': custom_widgets.CheckBoxInput()
        }


class ImageForm(forms.ModelForm): 
    class Meta:
        model = models.Image
        fields = ['name', 'url', 'variant', 'main_image']
        widgets = {
            'name': custom_widgets.TextInput(attrs={'placeholder': 'Name'}),
            'url': custom_widgets.TextInput(attrs={'placeholder': 'Url'}),
            'variant': custom_widgets.TextInput(attrs={'placeholder': 'Variant'}),
            'main_image': custom_widgets.CheckBoxInput()
        }

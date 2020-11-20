from django.contrib.auth import get_user_model
from django.db import models
from django.shortcuts import reverse

from store.choices import IndustryChoices, StoreCurrencies
from store.utils import get_product_model

MYUSER = get_user_model()

class PaymentOption(models.Model):
    reference = None
    store   = models.OneToOneField('Store', on_delete=models.CASCADE, blank=True, null=True)
    store_currency  = models.CharField(max_length=10, choices=StoreCurrencies.choices, default=StoreCurrencies.EUR)
    tax_rate   = models.IntegerField(default=20)
    
    stripe_live_key     = models.CharField(max_length=100, blank=True)
    stripe_secret_key   = models.CharField(max_length=100, blank=True)
    
    amazon_pay_key      = models.CharField(max_length=100, blank=True)
    enable_amazon_pay   = models.BooleanField(default=False)
    
    enable_apple_pay    = models.BooleanField(default=False)
    enable_google_pay   = models.BooleanField(default=False)

    def __str__(self):
        return self.store_currency


class Analytic(models.Model):
    reference = None
    store           = models.OneToOneField('Store', on_delete=models.CASCADE, blank=True, null=True)
    google_analytics = models.CharField(max_length=50, blank=True, null=True)
    google_tag_manager   = models.CharField(max_length=50, blank=True, null=True)
    google_optimize     = models.CharField(max_length=50, blank=True, null=True)
    google_ads      = models.CharField(max_length=50, blank=True, null=True)
    facebook_pixels     = models.CharField(max_length=50, blank=True, null=True)
    mailchimp       = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['google_analytics'])
        ]

    def __str__(self):
        return self.reference


class Store(models.Model):
    user = models.ForeignKey(MYUSER, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=50)

    products = models.ManyToManyField(get_product_model(), blank=True)

    contact_email = models.EmailField(max_length=100)
    customer_care_email = models.EmailField(max_length=100)
    
    store_industry = models.CharField(max_length=50, choices=IndustryChoices.choices, default=IndustryChoices.FASHION)
    
    legal_name = models.CharField(max_length=50, blank=True, null=True)
    telephone   = models.CharField(max_length=10, blank=True, null=True)
    address     = models.CharField(max_length=100, blank=True, null=True)
    city        = models.CharField(max_length=50, blank=True, null=True)
    zip_code    = models.CharField(max_length=5, blank=True, null=True)
    
    accounts_disabled    = models.BooleanField(default=True, help_text='The user can purchase even if he has an account')
    accounts_optional    = models.BooleanField(default=True, help_text='The user can purchase either as a registered or anonymous user')

    mobile_banner       = models.BooleanField(default=False, help_text='Show the mobile top banner')
    nav_banner       = models.BooleanField(default=False, help_text='Show the banner just below the navigation bar')

    automatic_archive     = models.BooleanField(default=False, help_text='Archive an order automatically after it has been fulfilled and paid')

    allow_coupons       = models.BooleanField(default=False)
    allow_accounts      = models.BooleanField(default=False)

    active      = models.BooleanField(default=False)
    on_hold     = models.BooleanField(default=False, help_text='Can access the store but cannot perform any actions')

    created_on = models.DateField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['name'])
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:products', args=[self.pk])


class Supplier(models.Model):
    store   = models.ForeignKey(Store, on_delete=models.CASCADE)
    name      = models.CharField(max_length=100, blank=True, null=True)
    country     = models.CharField(max_length=80, blank=True, null=True)
    email      = models.EmailField(max_length=100, blank=True, null=True)
    website      = models.URLField(max_length=100, blank=True, null=True)
    archive   = models.BooleanField(default=False)
    created_on  = models.DateField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.name

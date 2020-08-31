from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import fields, signals
from django.dispatch import receiver

MYUSER = get_user_model()

class DashboardSetting(models.Model):
    myuser    = models.OneToOneField(MYUSER, on_delete=models.CASCADE)
    dark_mode = fields.BooleanField(default=False)

    name = models.CharField(max_length=50)

    contact_email = models.EmailField(max_length=100)
    customer_care_email = models.EmailField(max_length=100)

    #     class IndustryChoices(models.Choices):
    #           FASHION   = 'Fashion'
    #           CLOTHING  = 'clothing'
    #           JEWELRY  = 'jewelry'
    #     store_industry      = models.CharField(max_length=50, choices=IndustryChoices.choices, default=IndustryChoices.FASHION)

    legal_name = models.CharField(max_length=50, blank=True, null=True)
    telephone = models.CharField(max_length=10, blank=True, null=True)
    #     address     = models.CharField(max_length=100, blank=True, null=True)
    #     city        = models.CharField(max_length=50, blank=True, null=True)
    #     zip_code    = models.CharField(max_length=5, blank=True, null=True)

    class StoreCurrencies(models.Choices):
        EUR = 'eur'
        DOLLARS = 'dollars'
    store_currency = models.CharField(
        max_length=10, choices=StoreCurrencies.choices, default=StoreCurrencies.EUR)
    tax_rate = models.IntegerField(default=20)

    #     stripe_live_key     = models.CharField(max_length=100, blank=True)
    #     stripe_secret_key   = models.CharField(max_length=100, blank=True)

    #     amazon_pay_key      = models.CharField(max_length=100, blank=True)
    #     enable_amazon_pay   = models.BooleanField(default=False)

    #     enable_apple_pay    = models.BooleanField(default=False)
    #     enable_google_pay   = models.BooleanField(default=False)

    #     accounts_disabled    = models.BooleanField(default=True, help_text='The user can purchase even if he has an account')
    #     accounts_optional    = models.BooleanField(default=True, help_text='The user can purchase either as a registered or anonymous user')

    #     mobile_banner       = models.BooleanField(default=False, help_text='Show the mobile top banner')
    #     nav_banner       = models.BooleanField(default=False, help_text='Show the banner just below the navigation bar')

    automatic_archive = models.BooleanField(
        default=False, help_text='Archive an order automatically after it has been fulfilled and paid')

    google_analytics        = models.CharField(max_length=50, blank=True, null=True)
    google_tag_manager  = models.CharField(max_length=50, blank=True, null=True)
    google_optimize     = models.CharField(max_length=50, blank=True, null=True)
    google_ads      = models.CharField(max_length=50, blank=True, null=True)
    facebook_pixels       = models.CharField(max_length=50, blank=True, null=True)
    mailchimp      = models.CharField(max_length=50, blank=True, null=True)

    allow_coupons = models.BooleanField(default=False)
    allow_accounts = models.BooleanField(default=False)

    # active      = models.BooleanField(default=False)
    # on_hold     = models.BooleanField(default=False, help_text='Can access the store but cannot perform any actions')

    
    objects = models.Manager()

    def __str__(self):
        return self.myuser.email

@receiver(signals.post_save, sender=MYUSER)
def create_user_dashboard(instance, sender, created, **kwargs):
    if created:
        DashboardSetting.objects.create(myuser=instance)

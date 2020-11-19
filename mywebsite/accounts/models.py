import stripe
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts import managers


class MyUser(AbstractBaseUser):
    """Base user model for those user accounts"""
    email       = models.EmailField(max_length=255, unique=True)
    firstname      = models.CharField(max_length=100, null=True, blank=True)
    lastname         = models.CharField(max_length=100, null=True, blank=True)
    
    is_active        = models.BooleanField(default=True)
    is_admin            = models.BooleanField(default=False)
    is_staff            = models.BooleanField(default=False)
    
    objects = managers.MyUserManager()

    USERNAME_FIELD      = 'email'
    REQUIRED_FIELDS     = []

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def get_full_name(self):
        return f'{self.firstname} {self.lastname}' 

    @property
    def get_short_name(self):
        return self.firstname

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)


class MyUserProfile(models.Model):
    """User profile model used to complete the base user model"""
    myuser              = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    customer_id           = models.CharField(max_length=100, blank=True, null=True, help_text='Stripe customer ID')
    birthdate         = models.DateField(default=timezone.now, blank=True, null=True)
    telephone           = models.CharField(max_length=20, blank=True, null=True)
    address            = models.CharField(max_length=150, blank=True, null=True)
    city               = models.CharField(max_length=100, blank=True, null=True)
    zip_code           = models.IntegerField(blank=True, null=True)

    objects = models.Manager()

    def __str__(self):
        return self.myuser.email

    @property
    def get_full_address(self):
        return f'{self.address}, {self.city}, {self.zip_code}'

    def clean(self, *args, **kwargs):
        try:
            details = stripe.Customer.create(
                email=self.myuser.email, 
                name=self.myuser.get_full_name
            )
        except stripe.error.StripeError as e:
            pass
        else:
            self.customer_id = details['customer_id']


# #####################
#       SIGNALS
# #####################

@receiver(post_save, sender=MyUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        MyUserProfile.objects.create(myuser=instance)

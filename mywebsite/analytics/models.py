from django.db import models
from analytics import utils


class AbstractAnalytic(models.Model):
    reference = models.CharField(max_length=70, default=utils.create_analytics_reference())
    user = None

    class Meta:
        abstract = True


class Analytic(AbstractAnalytic):
    google_analytics = models.CharField(max_length=50, blank=True, null=True, unique=True)
    google_tag_manager = models.CharField(max_length=50, blank=True, null=True, unique=True)
    google_optimize = models.CharField(max_length=50, blank=True, null=True, unique=True)
    google_ads = models.CharField(max_length=50, blank=True, null=True, unique=True)
    facebook_pixels = models.CharField(max_length=50, blank=True, null=True, unique=True)
    mailchimp = models.CharField(max_length=50, blank=True, null=True, unique=True)
    modified_on = models.DateField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['reference', 'google_analytics'])
        ]

    def __str__(self):
        return self.reference

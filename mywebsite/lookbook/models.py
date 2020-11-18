from django.db import models
from django.shortcuts import reverse
from django.utils import timezone

from lookbook.utilities import get_product_model


class LookBook(models.Model):
    """
    Lookbook for the store
    """
    name = models.CharField(max_length=70)
    products = models.ManyToManyField(get_product_model())
    created_on = models.DateField(default=timezone.now)

    objects = models.Manager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('lookbook:home')

from django.contrib.auth import get_user_model
from django.db import models
from shop.models import Product
from reviews.managers import ReviewManager

MYUSER = get_user_model()

class Review(models.Model):
    """
    Represents a customer review
    """
    user    = models.ForeignKey(MYUSER, blank=True, null=True, on_delete=models.SET_NULL)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL ,blank=True, null=True)
    rating  = models.IntegerField(default=1)
    text    = models.TextField(max_length=300)
    created_on  = models.DateTimeField(auto_now_add=True)

    objects = ReviewManager.as_manager()

    def __str__(self):
        return self.user.get_full_name

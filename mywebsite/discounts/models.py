from django.db import models
from django.shortcuts import reverse
from django.utils import timezone

from discounts import choices, utilities

PRODUCT_MODEL = utilities.get_product_model()

COLLECTION_MODEL = utilities.get_product_collection_model()

class Discount(models.Model):
    """
    A set of discounts applicable for a collection, a product
    or  a purchase
    """
    code        = models.CharField(max_length=10, default=utilities.create_discount_code())
    value       = models.IntegerField(default=5)
    value_type  = models.CharField(max_length=50, choices=choices.ValueTypes.choices, default=choices.ValueTypes.PERCENTAGE)

    product     = models.ForeignKey(PRODUCT_MODEL, blank=True, null=True, on_delete=models.SET_NULL, help_text='Apply on a specific product')
    collection = models.ForeignKey(COLLECTION_MODEL, help_text='Apply on an entire collection', on_delete=models.SET_NULL, blank=True, null=True)
    on_entire_order =   models.BooleanField(default=False, help_text='Apply on an entire order')

    minimum_purchase = models.IntegerField(default=0)
    minimum_quantity = models.IntegerField(default=0)

    usage_limit  = models.IntegerField(default=0, help_text='Number of times a code can be used in total')

    active      = models.BooleanField(default=False)

    start_date  = models.DateTimeField()
    end_date    = models.DateTimeField()

    created_on = models.DateField(auto_now_add=True)

    objects = models.Manager()

    def __str__(self):
        return self.code

    def get_promotion_url(self):
        """Returns a special link for a product that would have
        been marked as a special offer
        """
        if self.product:
            return reverse('discounts:offer', args=[self.code, self.product.reference])
        return None

    @property
    def is_valid(self):
        if self.end_date >= timezone.now():
            return all([False, self.active])
        return all([True, self.active])

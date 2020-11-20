from django.contrib.auth import get_user_model
from django.db import models
from django.shortcuts import reverse
from django.utils.functional import cached_property
from django.utils import timezone

from cart import validators, utilities, managers


MYUSER = get_user_model()

PRODUCT_MODEL = utilities.get_product_model()

PRODUCT_COLLECTION_MODEL = utilities.get_product_collection_model()

DISCOUNT_MODEL = utilities.get_discount_model()


class AbstractCart(models.Model):
    cart_id     = models.CharField(max_length=80)
    product     = models.ForeignKey(PRODUCT_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    
    price_pre_tax    = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Price excluding taxes')
    price_post_tax   = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='Price including taxes')
    
    color       = models.CharField(max_length=50)
    size       = models.CharField(max_length=5, validators=[validators.generic_size_validator], blank=True, null=True)
    quantity    = models.IntegerField(default=1, validators=[validators.quantity_validator])
    anonymous   = models.BooleanField(default=False)

    paid_for    = models.BooleanField(default=False)

    created_on = models.DateField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        abstract = True

    def __str__(self):
        return self.cart_id

    @cached_property
    def get_product_total(self):
        try:
            return self.price_post_tax * self.quantity
        except:
            return 0

    def get_increase_quantity_url(self):
        return reverse('cart:alter_quantity', args=['add'])

    def get_decrease_quantity_url(self):
        return reverse('cart:alter_quantity', args=['reduce'])

    def get_total(self):
        if self.price_incl_taxes and self.quantity:
            return self.price_incl_taxes * self.quantity
        return 0

    def has_orders(self):
        orders = self.customerorder_set.all()
        return orders.exists()


class Cart(AbstractCart):
    """
    Represents a customer's cart
    """
    cart_manager = managers.CartManager.as_manager()
    statistics  = managers.CartsStatisticsManager.as_manager()

    class Meta:
        ordering = ['-created_on', '-pk']
        indexes = [
            models.Index(fields=['price_pre_tax', 'quantity']),
        ]

    def __str__(self):
        return self.cart_id

    def clean(self):
        if self.price_pre_tax is not None:
            if self.price_pre_tax > 0:
                self.price_post_tax = utilities\
                    .calculate_vat(self.price_pre_tax, vat=20)
            else:
                return 0


class CustomerOrder(models.Model):
    """
    Represents a customer's order
    """
    user        = models.ForeignKey(MYUSER, blank=True, null=True, on_delete=models.SET_NULL)
    cart             = models.ManyToManyField(Cart, blank=True)
    reference  = models.CharField(max_length=50)
    transaction   = models.CharField(max_length=200, default=utilities.create_transaction_token())
    payment           = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    accepted        = models.BooleanField(default=False)
    shipped       = models.BooleanField(default=False)
    refund        = models.BooleanField(default=False)

    comment       = models.TextField(max_length=500, blank=True, null=True)

    class DeliveryChoices(models.Choices):
        STANDARD = 'standard'
        PRIME = 'prime'
    delivery    = models.CharField(
        max_length=50, 
        choices=DeliveryChoices.choices, 
        default=DeliveryChoices.STANDARD
    )

    created_on  = models.DateField(auto_now_add=True)

    objects = models.Manager()
    statistics  = managers.OrdersStatisticsManager.as_manager()

    class Meta:
        ordering = ['-created_on', '-pk']
        indexes = [
            models.Index(fields=['payment'])
        ]

    def __str__(self):
        return self.transaction


class Shipment(models.Model):
    """
    Tracking orders that are shipped
    """
    customer_order = models.ForeignKey(CustomerOrder, on_delete=models.CASCADE)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    completed       = models.BooleanField(default=False)

    created_on = models.DateField(auto_now_add=True)

    objects = models.Manager()

    def __str__(self):
        return self.customer_order.transaction

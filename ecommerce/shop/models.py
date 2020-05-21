from django.db import models
from shop import managers
from django.shortcuts import reverse
from shop import validators
import datetime

class Image(models.Model):
    name    = models.CharField(max_length=50)
    url     = models.URLField(blank=True, null=True)

    objects = models.Manager()
    image_manager = managers.ImageManager.as_manager()

    class Meta:
        indexes = [
            models.Index(fields=['url']),
        ]

    def __str__(self):
        return self.name

class Collection(models.Model):
    name      = models.CharField(max_length=50)

    objects = models.Manager()
    collection_manager = managers.CollectionManager.as_manager()
    forms_manager = managers.FormsManager.as_manager()

    def __str__(self):
        return self.name

class Product(models.Model):
    """Model for products"""
    collection      = models.ForeignKey(Collection, on_delete=models.DO_NOTHING)
    images          = models.ManyToManyField(Image)
    name          = models.CharField(max_length=50, blank=True, null=True)
    price_ht    = models.DecimalField(max_digits=3, decimal_places=2)
    slug        = models.SlugField()

    objects = models.Manager()
    product_manager = managers.ProductManager.as_manager()

    class Meta:
        indexes = [
            models.Index(fields=['collection']),
        ]

    def __str__(self):
        return self.collection.name

    @property
    def get_absolute_url(self):
        collection_name = self.collection.name.lower()
        return reverse('product', args=['femme', collection_name, self.pk, self.slug])

    @property
    def get_main_image_url(self):
        return self.images.all().first().url

class AbstractCart(models.Model):
    """Customer's cart"""
    product     = models.ManyToManyField(Product, blank=True)
    price_ht    = models.DecimalField(max_digits=5, decimal_places=2)
    quantity    = models.IntegerField(default=1)
    cart_id         = models.CharField(max_length=20)
    anonymous   = models.BooleanField(default=False)

    objects = models.Manager()
    cart_manager = managers.CartManager.as_manager()

    class Meta:
        abstract = True

class Cart(AbstractCart):
    """Cart for registered users"""
    # cart_manager = managers.CartsManager.as_manager()

    class Meta:
        indexes = [
            models.Index(fields=['price_ht', 'quantity']),
        ]

    def __str__(self):
        return self.cart_id

    @property
    def get_product_total(self):
        return self.price_ht * self.quantity

class CustomerOrder(models.Model):
    """Customer order's"""
    cart             = models.ForeignKey(Cart, blank=True, null=True, on_delete=models.CASCADE)
    customer_order_id = models.CharField(max_length=20)

    objects = models.Manager()
    order_manager = managers.OrdersManager.as_manager()

    def __str__(self):
        return self.customer_order_id

class Shipment(models.Model):
    """Tracking orders that are shipped"""
    customer_order = models.ForeignKey(CustomerOrder, on_delete=models.CASCADE)

    objects = models.Manager()
    shipment_manager = managers.ShipmentManager.as_manager()

    def __str__(self):
        return self.customer_order.customer_order_id

class PromotionalCode(models.Model):
    """Model for promotion codes"""
    code = models.CharField(max_length=4, default='')
    product = models.ManyToManyField(Product, blank=True)
    collection = models.ManyToManyField(Collection, blank=True)
    end_date = models.DateField()

    def __str__(self):
        return self.code

    @property
    def is_valid(self):
        if not self.end_date:
            return False
        current_date = datetime.datetime.now()
        if self.end_date > current_date:
            return False
        return True
import datetime

from django.db import models
from django.shortcuts import reverse

from shop import managers, utilities, validators


class Image(models.Model):
    name    = models.CharField(max_length=50)
    url     = models.URLField(blank=True, null=True)
    variant = models.CharField(max_length=30, default='Noir')

    aws_key   = models.CharField(max_length=50, null=True, blank=True, verbose_name='AWS folder key')
    image_url = models.URLField(null=True, blank=True)

    main_image  = models.BooleanField(default=False, help_text='Indicates if this is the main image for the product')
    
    objects = models.Manager()
    image_manager = managers.ImageManager.as_manager()

    class Meta:
        indexes = [
            models.Index(fields=['url']),
        ]

    def __str__(self):
        return self.name

class ProductCollection(models.Model):
    name      = models.CharField(max_length=50)

    class GenderChoices(models.Choices):
        FEMME = 'femme'
        HOMME = 'homme'
    gender = models.CharField(max_length=50, choices=GenderChoices.choices, default=GenderChoices.FEMME)
    
    view_name   = models.CharField(max_length=50)
    image       = models.URLField(blank=True, null=True)
    presentation_text = models.TextField(max_length=300, blank=True, null=True)
    show_presentation  = models.BooleanField(default=False)

    objects = models.Manager()
    collection_manager = managers.CollectionManager.as_manager()
    forms_manager = managers.FormsManager.as_manager()

    def __str__(self):
        return self.name

    def clean(self):
        if self.name:
            self.view_name = self.name.lower()

class ClotheSize(models.Model):
    name                = models.CharField(max_length=3, validators=[validators.size_validator])
    verbose_name               = models.CharField(max_length=50)
    chest_circumference     = models.PositiveIntegerField()
    waist_hip_circumference    = models.PositiveIntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['name'])
        ]

    def __str__(self):
        return self.verbose_name

class Product(models.Model):
    name          = models.CharField(max_length=50, blank=True, null=True)
    reference   = models.CharField(max_length=30, default=utilities.create_product_reference())
    class GenderChoices(models.Choices):
        FEMME = 'femme'
        HOMME = 'homme'
    gender = models.CharField(max_length=50, choices=GenderChoices.choices, default=GenderChoices.FEMME)

    images          = models.ManyToManyField(Image)
    collection      = models.ForeignKey(ProductCollection, on_delete=models.DO_NOTHING)
    clothe_size        = models.ManyToManyField(ClotheSize, blank=True)
    description   = models.TextField(max_length=280, blank=True, null=True)

    price_ht    = models.DecimalField(max_digits=5, decimal_places=2)
    discount_pct    = models.IntegerField(default=0, validators=[validators.discount_pct_validator])
    discounted_price   = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    price_valid_until = models.DateField(default=utilities.add_to_current_date(d=30))

    sku      = models.CharField(max_length=50, blank=True, null=True, help_text='ex. BCLOGO-GRIS-SMA')

    in_stock     = models.BooleanField(default=True)
    discounted  = models.BooleanField(default=False)
    our_favorite    = models.BooleanField(default=False)
    active      = models.BooleanField(default=False)

    slug        = models.SlugField()
    
    last_modified   = models.DateField(auto_now=True)
    created_on = models.DateField(auto_now_add=True)

    objects = models.Manager()
    product_manager = managers.ProductManager.as_manager()

    class Meta:
        ordering = ['-created_on']
        indexes = [
            models.Index(fields=['reference', 'collection', 'name']),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        if self.discount_pct > 0:
            self.discounted_price = utilities.\
                    calculate_discount(self.price_ht, self.discount_pct)

    def get_absolute_url(self):
        collection_name = self.collection.name.lower()
        return reverse('product', args=['femme', collection_name, self.pk, self.slug])

    def get_dashboard_absolute_url(self):
        return reverse('dashboard_product', args=[self.pk])

    @property
    def get_main_image_url(self):
        """Returns the url of the image marked as main"""
        images = self.images.filter(main_image=True)
        if images.exists():
            return images.first().url
        return []

    def get_product_images(self):
        """Get all the product's images"""
        return self.images.all()

    @property
    def is_novelty(self):
        """Tells if the product was created less than 7 days ago"""
        current_date = datetime.datetime.now().date()
        date_fifteen_days_ago = self.created_on - datetime.timedelta(days=7)
        return all([self.created_on >= date_fifteen_days_ago, \
                                    self.created_on <= current_date])

    def get_price(self):
        """Chooses between the price ht and the
        discounted price if there is a discount
        """
        if self.discounted and \
            self.discounted_price > 0:
                return self.discounted_price
        return self.price_ht

    def is_discounted(self):
        """Says whether the product is discounted or not"""
        return self.discounted

    @property
    def get_discount_pct_as_text(self):
        if self.discounted:
            return f'-{self.discount_pct}%'

class PromotionalCode(models.Model):
    code        = models.CharField(max_length=4)
    value       = models.IntegerField(default=5)
    product     = models.ManyToManyField(Product, blank=True)
    collection = models.ManyToManyField(ProductCollection, blank=True)
    active      = models.BooleanField(default=False)
    end_date    = models.DateField()
    created_on = models.DateField(auto_now_add=True)

    objects = models.Manager()

    def __str__(self):
        return self.code

    @property
    def is_valid(self):
        current_date = datetime.datetime.now().date()
        if self.end_date >= current_date:
            return all([False, self.active])
        return all([True, self.active])

class Cart(models.Model):
    cart_id         = models.CharField(max_length=80)
    product     = models.ForeignKey(Product, blank=True, null=True, on_delete=models.CASCADE)
    coupon      = models.ForeignKey(PromotionalCode, on_delete=models.SET_NULL, blank=True, null=True)
    
    price_ht    = models.DecimalField(max_digits=5, decimal_places=2)
    price_ttc   = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    color       = models.CharField(max_length=50)
    size       = models.CharField(max_length=30, blank=True, null=True, \
                                    validators=[validators.size_validator])
    quantity    = models.IntegerField(default=1, validators=[validators.quantity_validator])
    anonymous   = models.BooleanField(default=False)

    created_on = models.DateField(auto_now_add=True)

    objects = models.Manager()
    cart_manager = managers.CartManager.as_manager()
    statistics  = managers.CartsStatisticsManager.as_manager()

    class Meta:
        ordering = ['-product__name']
        indexes = [
            models.Index(fields=['price_ht', 'quantity']),
        ]

    def __str__(self):
        return self.cart_id

    def clean(self):
        if self.price_ht > 0:
            self.price_ttc = utilities\
                    .calculate_tva(self.price_ht, tva=20)

    @property
    def get_product_total(self):
        return self.price_ht * self.quantity

    def get_increase_quantity_url(self):
        return reverse('alter_quantity', args=['add'])

    def get_decrease_quantity_url(self):
        return reverse('alter_quantity', args=['reduce'])

    def has_coupon(self):
        return self.coupon is not None

class CustomerOrder(models.Model):
    cart             = models.ManyToManyField(Cart, blank=True)
    reference  = models.CharField(max_length=50)
    transaction   = models.CharField(max_length=200, default=utilities.create_transaction_token())
    payment           = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    completed       = models.BooleanField(default=False)

    created_on      = models.DateField(auto_now_add=True)

    objects = models.Manager()
    statistics  = managers.OrdersStatisticsManager.as_manager()

    class Meta:
        ordering = ['-created_on']
        indexes = [
            models.Index(fields=['payment'])
        ]

    def __str__(self):
        return self.transaction

class Shipment(models.Model):
    """Tracking orders that are shipped"""
    customer_order = models.ForeignKey(CustomerOrder, on_delete=models.CASCADE)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    completed       = models.BooleanField(default=False)

    created_on = models.DateField(auto_now_add=True)

    objects = models.Manager()

    def __str__(self):
        return self.customer_order.transaction

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Product)
def create_slug(instance, sender, created, **kwargs):
    if created:
        if instance.name:
            instance.slug = utilities.create_product_slug(instance.name)
            instance.save()
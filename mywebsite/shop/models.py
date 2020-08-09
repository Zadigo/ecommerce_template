import datetime

from django import utils
from django.contrib.auth import get_user_model
from django.core import exceptions
from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import reverse
from django.utils import timezone
from django.utils.functional import cached_property

from mywebsite import aws_manager
from shop import managers, utilities, validators

MYUSER = get_user_model()

class Image(models.Model):
    """
    Represents an image for a given product
    """
    name    = models.CharField(max_length=50)
    variant = models.CharField(max_length=30, default='Noir')
    aws_key   = models.CharField(max_length=50, null=True, blank=True, verbose_name='AWS folder key')
    aws_slug_name   = models.CharField(max_length=100, blank=True, null=True, help_text='File name on AWS')    
    aws_image =    models.BooleanField(default=False)
    main_image  = models.BooleanField(default=False, help_text='Indicates if this is the main image for the product')
    url     = models.URLField(blank=True, null=True)

    objects = models.Manager()
 
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['url']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('manage_image', args=[self.pk])

    def clean(self):
        if self.name and self.aws_image:
            # Create a slug version of the image such as
            # product_name and add .jpg to it
            self.aws_slug_name = f"{self.name.replace(' ', '_').lower()}.jpg"

            if not self.aws_key:
                raise exceptions.ValidationError('You must provide an AWS key when trying to create an AWS image')

            object_path = f'mywebsite/products/{self.aws_key}/{self.aws_slug_name}'
            self.url = aws_manager.aws_url_for(object_path)


class AutomaticCollectionCriteria(models.Model):
    """
    Model that stores conditions of classifying products automatically
    under a specific collection
    """
    reference = models.CharField(max_length=50, default=utilities.create_reference())

    class ConditionsChoices(models.Choices):
        IS_EQUAL_TO = 'is equal to'
        IS_NOT_EQUAL_TO = 'is not equal to'
        IS_GREAT_THAN = 'is greater than'
        IS_LESS_THAN = 'is less than'
        STARTS_WITH  = 'starts with'
        ENDS_WITH    = 'ends with'
        CONTAINS        = 'contains'
        DOES_NOT_CONTAIN = 'does not contain'
        YES         = 'yes'
        NO      = 'no'
    condition    = models.CharField(max_length=50, choices=ConditionsChoices.choices, default=ConditionsChoices.IS_EQUAL_TO)
    value       = models.CharField(max_length=50)

    modified_on = models.DateField(auto_now=True)
    created_on = models.DateField(auto_now_add=True)

    objects = models.Manager()

    def __str__(self):
        return self.reference


class ProductCollection(models.Model):
    """
    Represents a collection of products
    """
    name      = models.CharField(max_length=50)

    class GenderChoices(models.Choices):
        FEMME = 'femme'
        HOMME = 'homme'
    gender = models.CharField(max_length=50, choices=GenderChoices.choices, default=GenderChoices.FEMME)
    
    view_name   = models.CharField(max_length=50)
    image       = models.URLField(blank=True, null=True)
    presentation_text = models.TextField(max_length=300, blank=True, null=True)
    google_description = models.CharField(max_length=160, blank=True, null=True)
    show_presentation  = models.BooleanField(default=False)

    automatic = models.BooleanField(default=False)
    criterion     = models.ManyToManyField(AutomaticCollectionCriteria, blank=True)

    objects = models.Manager()
    collection_manager = managers.CollectionManager.as_manager()

    def __str__(self):
        return self.name

    def clean(self):
        if self.name:
            self.view_name = self.name.replace(' ', '').lower()


class Variant(models.Model):
    """
    Model for variants such as the size of an item
    """
    name                = models.CharField(max_length=3, validators=[validators.generic_size_validator], blank=True, null=True)
    verbose_name          = models.CharField(max_length=50, blank=True, null=True)

    in_stock        = models.BooleanField(default=True)
    active        = models.BooleanField(default=False)
    
    objects     = models.Manager()

    class Meta:
        indexes = [
            models.Index(fields=['name'])
        ]

    def __str__(self):
        return self.name

class Product(models.Model):
    """
    This model represents a product in the database. It is composed
    of three main components that should be implemented before creation:
        
        - Name
        - Reference
        - Creation
        - Collection
        - Price pre-tax
        - Price post-tax

    For better organization, products are enforced as being part of a
    collection. So before creating a product, a collection should already
    exist.
    
    NOTE: The Reference field while required has a default that comes from
    `create_product_reference` definition from the `utilities` module.
    """
    name          = models.CharField(max_length=50, blank=True, null=True)
    reference   = models.CharField(max_length=30, default=utilities.create_product_reference())
    class GenderChoices(models.Choices):
        FEMME = 'femme'
        HOMME = 'homme'
    gender = models.CharField(max_length=50, choices=GenderChoices.choices, default=GenderChoices.FEMME)

    images          = models.ManyToManyField(Image)
    collection      = models.ForeignKey(ProductCollection, on_delete=models.DO_NOTHING)
    variant        = models.ManyToManyField(Variant, blank=True)

    description   = models.TextField(max_length=280, blank=True, null=True)
    description_html = models.TextField(max_length=800, blank=True, null=True)
    description_objects  = models.TextField(max_length=800, blank=True, null=True)

    price_ht    = models.DecimalField(max_digits=5, decimal_places=2)
    discount_pct    = models.IntegerField(default=10, blank=True)
    discounted_price   = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    price_valid_until = models.DateField(default=utilities.add_to_current_date(d=30))
    quantity        = models.IntegerField(default=0, blank=True)

    sku      = models.CharField(max_length=50, blank=True, null=True, help_text='ex. BCLOGO-GRIS-SMA')

    class GoogleProductCategory(models.Choices):
        SKIRTS = '5424'
        TOPS = '212'
        SHORTS = '207'
        DRESSES = '2271'
        BRAS = '214'
        ACCESSORIES = '178'
        FLYINGTOYACCESSORIES = '7366'
    google_category = models.CharField(max_length=5,
        choices=GoogleProductCategory.choices, default=GoogleProductCategory.TOPS)

    # is_top_garment       = models.BooleanField(default=True)
    # is_lower_garment   = models.BooleanField(default=False)
    # is_bra        = models.BooleanField(default=False)
    # is_shoe       = models.BooleanField(default=False)
    # is_underwear  = models.BooleanField(default=False)

    in_stock     = models.BooleanField(default=True)
    discounted  = models.BooleanField(default=False)
    our_favorite    = models.BooleanField(default=False)
    active      = models.BooleanField(default=False)
    private     = models.BooleanField(default=False, help_text='Product is on accessible by sharing the direct link')

    slug        = models.SlugField()
    
    to_be_published_on = models.DateField(default=timezone.now, blank=True)
    last_modified   = models.DateField(auto_now=True)
    created_on = models.DateField(auto_now_add=True)

    objects = models.Manager()
    product_manager = managers.ProductManager.as_manager()

    class Meta:
        ordering = ['-created_on', '-pk']
        indexes = [
            models.Index(fields=['reference', 'collection', 'name']),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        if self.discount_pct is None:
            self.discounted_price = 0
        elif self.discount_pct > 0:
            self.discounted_price = utilities.\
                    calculate_discount(self.price_ht, self.discount_pct)
        
        if self.name:
            new_slug = utilities.create_product_slug(self.name)
            self.slug = new_slug

    @cached_property
    def get_main_image_url(self):
        """Returns the url of the image marked as main"""
        images = self.images.filter(main_image=True)
        if images.exists():
            image = images.first()
            return image.url
        else:
            try:
                # In case no main image was marked
                # then try to return the first image -;
                # However, there can be an exceptional
                # case where the product has no image
                # and in which case, we have to protect
                # against a NoneType error
                return images.first().url
            except AttributeError:
                return None

    @property
    def is_novelty(self):
        """Tells if the product was created less than 5 days ago"""
        current_date = datetime.datetime.now().date()
        date_five_days_ago = current_date - datetime.timedelta(days=5)
        return all([self.created_on >= date_five_days_ago, self.created_on <= current_date])

    @property
    def is_discounted(self):
        """Says whether the product is discounted or not"""
        return self.discounted

    def get_absolute_url(self):
        collection_name = self.collection.name.lower()
        return reverse('product', args=['femme', collection_name, self.pk, self.slug])

    def get_preview_url(self):
        return reverse('preview', args=[self.pk, self.slug])
    
    def get_private_url(self):
        return reverse('private', args=[self.pk, self.slug])

    def get_collection_url(self):
        return reverse('collection', args=[self.gender, self.collection.view_name])
    
    # @utils.functional.cached_property
    def get_product_images(self):
        return self.images.all()

    def get_price(self):
        """Chooses between the price ht and the
        discounted price if there is a discount
        """
        if self.discounted_price is None:
            return self.price_ht
        elif self.discounted_price > 0 and self.discounted:
            return self.discounted_price
        else:
            return self.price_ht


class Discount(models.Model):
    """
    A set of discounts applicable for a collection, a product
    or  a purchase
    """
    code        = models.CharField(max_length=10, default=utilities.create_discount_code())
    value       = models.IntegerField(default=5)
    class ValueTypes(models.Choices):
        PERCENTAGE      = 'percentage'
        FIXED_AMOUNT     = 'fixed amount'
        FREE_SHIPPING = 'free shipping'
    value_type  = models.CharField(max_length=50, choices=ValueTypes.choices, default=ValueTypes.PERCENTAGE)

    product     = models.ForeignKey(Product, blank=True, null=True, on_delete=models.SET_NULL, help_text='Apply on a specific product')
    collection = models.ForeignKey(ProductCollection, help_text='Apply on an entire collection', on_delete=models.SET_NULL, blank=True, null=True)
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
            return reverse('special_offer', args=[self.code, self.product.reference])
        return None

    @property
    def is_valid(self):
        if self.end_date >= utils.timezone.now():
            return all([False, self.active])
        return all([True, self.active])


class Cart(models.Model):
    """
    Represents a customer's cart
    """
    cart_id         = models.CharField(max_length=80)
    product     = models.ForeignKey(Product, blank=True, null=True, on_delete=models.CASCADE)
    coupon      = models.ForeignKey(Discount, on_delete=models.SET_NULL, blank=True, null=True)
    
    price_ht    = models.DecimalField(max_digits=5, decimal_places=2)
    # discounted_price    = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    price_ttc   = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    color       = models.CharField(max_length=50)
    size       = models.CharField(max_length=5, validators=[validators.generic_size_validator], blank=True, null=True)
    quantity    = models.IntegerField(default=1, validators=[validators.quantity_validator])
    anonymous   = models.BooleanField(default=False)

    created_on = models.DateField(auto_now_add=True)

    objects = models.Manager()
    cart_manager = managers.CartManager.as_manager()
    statistics  = managers.CartsStatisticsManager.as_manager()

    class Meta:
        ordering = ['-created_on', '-pk']
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

    def get_total(self):
        if self.price_ht and self.quantity:
            return self.price_ht * self.quantity
        return 0

    def has_orders(self):
        orders = self.customerorder_set.all()
        if orders:
            return True
        return False


class CustomerOrder(models.Model):
    """
    Reprensents a customer's order
    """
    user        = models.ForeignKey(MYUSER, blank=True, null=True, on_delete=models.SET_NULL)
    cart             = models.ManyToManyField(Cart, blank=True)
    reference  = models.CharField(max_length=50)
    transaction   = models.CharField(max_length=200, default=utilities.create_transaction_token())
    payment           = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    accepted        = models.BooleanField(default=False)
    # TODO: Maybe move this field to shipment
    shipped       = models.BooleanField(default=False)
    # TODO: change to delivered or use the completed
    # field in the Shipment model
    completed       = models.BooleanField(default=False)
    refund        = models.BooleanField(default=False)

    comment       = models.TextField(max_length=500, blank=True, null=True)

    tracking_number     = models.CharField(max_length=50, blank=True, null=True)

    class DeliveryChoices(models.Choices):
        STANDARD = 'standard'
        # PRIME = 'prime'
    delivery    = models.CharField(max_length=50, choices=DeliveryChoices.choices, default=DeliveryChoices.STANDARD)

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


class Review(models.Model):
    """
    Represents a customer review
    """
    user    = models.ForeignKey(MYUSER, blank=True, null=True, on_delete=models.SET_NULL)
    customer_order = models.ForeignKey(CustomerOrder, on_delete=models.CASCADE ,blank=True, null=True)
    rating  = models.IntegerField(default=1)
    text    = models.TextField(max_length=300)
    created_on  = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.customer_order


class LookBook(models.Model):
    """
    Lookbook for the store
    """
    name    = models.CharField(max_length=70)
    products = models.ManyToManyField(Product)
    create_on = models.DateField(default=utils.timezone.now)

    def __str__(self):
        return self.name


# class Supplier(models.Model):
#     store   = models.ForeignKey(Store, on_delete=models.CASCADE)
#     name      = models.CharField(max_length=100, blank=True, null=True)
#     country     = models.CharField(max_length=80, blank=True, null=True)
#     email      = models.EmailField(max_length=100, blank=True, null=True)
#     website      = models.URLField(max_length=100, blank=True, null=True)

#     def __str__(self):
#         return self.name


@receiver(post_save, sender=Product)
def create_slug(instance, sender, created, **kwargs):
    if created:
        if instance.name:
            instance.slug = utilities.create_product_slug(instance.name)
            instance.save()

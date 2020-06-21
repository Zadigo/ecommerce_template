import datetime

from django import utils
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import reverse

from accounts import models as accounts_models
from shop import managers, utilities, validators


class Store(models.Model):
    store_name          = models.CharField(max_length=50)

    store_contact_email = models.EmailField(max_length=100)
    customer_care_email = models.EmailField(max_length=100)

    class IndustryChoices(models.Choices):
          FASHION   = 'Fashion'
          CLOTHING  = 'clothing'
          JEWELRY  = 'jewelry'
    store_industry      = models.CharField(max_length=50, choices=IndustryChoices.choices, default=IndustryChoices.FASHION)

    legal_name = models.CharField(max_length=50, blank=True, null=True)
    telephone   = models.CharField(max_length=10, blank=True, null=True)
    address     = models.CharField(max_length=100, blank=True, null=True)
    city        = models.CharField(max_length=50, blank=True, null=True)
    zip_code    = models.CharField(max_length=5, blank=True, null=True)

    class StoreCurrencies(models.Choices):
          EUR = 'eur'
          DOLLARS = 'dollars'
    currency  = models.CharField(max_length=10, choices=StoreCurrencies.choices, default=StoreCurrencies.EUR)
    tax_rate   = models.IntegerField(default=20)

    stripe_live_key     = models.CharField(max_length=100, blank=True)
    stripe_secret_key   = models.CharField(max_length=100, blank=True)

    amazon_pay_key      = models.CharField(max_length=100, blank=True)
    enable_amazon_pay   = models.BooleanField(default=False)

    enable_apple_pay    = models.BooleanField(default=False)
    enable_google_pay   = models.BooleanField(default=False)

    accounts_disabled    = models.BooleanField(default=True, help_text='The user can purchase even if he has an account')
    accounts_optional    = models.BooleanField(default=True, help_text='The user can purchase either as a registered or anonymous user')

    mobile_banner       = models.BooleanField(default=False, help_text='Show the mobile top banner')
    nav_banner       = models.BooleanField(default=False, help_text='Show the banner just below the navigation bar')

    automatic_archive     = models.BooleanField(default=False, help_text='Archive an order automatically after it has been fulfilled and paid')

    google_analytics_tag        = models.CharField(max_length=50, blank=True, null=True)
    google_tag_manager_tag  = models.CharField(max_length=50, blank=True, null=True)
    google_optimize_tag     = models.CharField(max_length=50, blank=True, null=True)
    google_ads_tag      = models.CharField(max_length=50, blank=True, null=True)
    facebook_pixels_tag       = models.CharField(max_length=50, blank=True, null=True)
    mailchimp_tag       = models.CharField(max_length=50, blank=True, null=True)

    allow_coupons       = models.BooleanField(default=False)

    def __str__(self):
        return self.store_name

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
        ordering = ['name']
        indexes = [
            models.Index(fields=['url']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('manage_image', args=[self.pk])

class AutomaticCollection(models.Model):
    reference = models.CharField(max_length=50)
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

    def __str__(self):
        return self.reference

class Collection(models.Model):
    store   = models.ForeignKey(Store, on_delete=models.SET_NULL, blank=True, null=True)
    name      = models.CharField(max_length=50)

    class GenderChoices(models.Choices):
        FEMME = 'femme'
        HOMME = 'homme'
    gender = models.CharField(max_length=50, choices=GenderChoices.choices, default=GenderChoices.FEMME)
    
    view_name   = models.CharField(max_length=50)
    image       = models.URLField(blank=True, null=True)
    presentation_text = models.TextField(max_length=300, blank=True, null=True)
    show_presentation  = models.BooleanField(default=False)

    automatic = models.BooleanField(default=False)
    criterion     = models.ManyToManyField(AutomaticCollection, blank=True)

    objects = models.Manager()
    collection_manager = managers.CollectionManager.as_manager()

    def __str__(self):
        return self.name

    def clean(self):
        if self.name:
            self.view_name = self.name.lower()

class ClotheSize(models.Model):
    name                = models.CharField(max_length=3, validators=[validators.size_validator])
    verbose_name               = models.CharField(max_length=50)

    # Sizes for tops, shirts...
    # front     = models.IntegerField(validators=[], default=0)
    # sleeve        = models.IntegerField(validators=[], default=0)
    # shoulder      =  models.IntegerField(validators=[], default=0)
    # chest        = models.IntegerField(validators=[], default=0, verbose_name='chest or bust width')
    # cross_shoulder =  models.IntegerField(validators=[], default=0)
    # Sizes for skirts, shorts...
    waist       =  models.IntegerField(validators=[], default=0, verbose_name='waist width')
    hip       =  models.IntegerField(validators=[], default=0)
    length      = models.IntegerField(validators=[], default=0)
    thigh       = models.IntegerField(validators=[], default=0)

    # is_top_clothe       = models.BooleanField(default=True)
    # is_lower_clothe   = models.BooleanField(default=False)

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
    collection      = models.ForeignKey(Collection, on_delete=models.DO_NOTHING)
    clothe_size        = models.ManyToManyField(ClotheSize, blank=True)

    description   = models.TextField(max_length=280, blank=True, null=True)

    price_ht    = models.DecimalField(max_digits=5, decimal_places=2)
    discount_pct    = models.IntegerField(default=0, validators=[validators.discount_pct_validator])
    discounted_price   = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    price_valid_until = models.DateField(default=utilities.add_to_current_date(d=30))

    sku      = models.CharField(max_length=50, blank=True, null=True, help_text='ex. BCLOGO-GRIS-SMA')

    class GoogleProductCategory(models.Choices):
        SKIRTS = '5424'
        TOPS = '212'
        SHORTS = '207'
        DRESSES = '2271'
        BRAS = '214'
        ACCESSORIES = '178'
        FLYINGTOYACCESSORIES = '7366'
    google_category = models.CharField(max_length=5, \
        choices=GoogleProductCategory.choices, default=GoogleProductCategory.TOPS)

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
        
        if self.name:
            new_slug = utilities.create_product_slug(self.name)
            self.slug = new_slug

    def get_absolute_url(self):
        collection_name = self.collection.name.lower()
        return reverse('product', args=['femme', collection_name, self.pk, self.slug])

    def get_dashboard_absolute_url(self):
        return reverse('dashboard_product', args=[self.pk])

    def get_collection_url(self):
        return reverse('collection', args=[self.gender, self.collection.view_name])

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
        date_five_days_ago = current_date - datetime.timedelta(days=5)
        return all([self.created_on >= date_five_days_ago, self.created_on <= current_date])

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

    def is_discounted(self):
        """Says whether the product is discounted or not"""
        return self.discounted

    @property
    def get_discount_pct_as_text(self):
        if self.discounted:
            return f'-{self.discount_pct}%'

class Review(models.Model):
    user   = models.ForeignKey(accounts_models.MyUser, blank=True, null=True, on_delete=models.SET_NULL)
    product =   models.ForeignKey(Product, on_delete=models.CASCADE)
    rating    = models.IntegerField(default=1, validators=[])
    text    = models.TextField(max_length=300)
    created_on  = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.product

class Discount(models.Model):
    code        = models.CharField(max_length=10, default=utilities.create_discount_code())
    value       = models.IntegerField(default=5)
    class ValueTypes(models.Choices):
        PERCENTAGE      = 'percentage'
        FIXED_AMOUNT     = 'fixed amount'
        FREE_SHIPPING = 'free shipping'
    value_type  = models.CharField(max_length=50, choices=ValueTypes.choices, default=ValueTypes.PERCENTAGE)

    product     = models.ForeignKey(Product, blank=True, null=True, \
                        on_delete=models.SET_NULL, help_text='Apply on a specific product')
    collection = models.ManyToManyField(Collection, blank=True,
                            help_text='Apply on an entire collection')
    on_entire_order =   models.BooleanField(default=False, \
                            help_text='Apply on an entire order')

    minimum_purchase = models.IntegerField(default=0)
    minimum_quantity = models.IntegerField(default=0)

    usage_limit  = models.IntegerField(default=0, \
                        help_text='Number of times a code can be used in total')

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
    cart_id         = models.CharField(max_length=80)
    product     = models.ForeignKey(Product, blank=True, null=True, on_delete=models.CASCADE)
    coupon      = models.ForeignKey(Discount, on_delete=models.SET_NULL, blank=True, null=True)
    
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
    user        = models.ForeignKey(accounts_models.MyUser, blank=True, null=True, on_delete=models.SET_NULL)
    cart             = models.ManyToManyField(Cart, blank=True)
    reference  = models.CharField(max_length=50)
    transaction   = models.CharField(max_length=200, default=utilities.create_transaction_token())
    payment           = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    accepted        = models.BooleanField(default=False)
    shipped       = models.BooleanField(default=False)
    # TODO: change to delivered
    completed       = models.BooleanField(default=False)
    refund        = models.BooleanField(default=False)

    tracking_number     = models.CharField(max_length=50, blank=True, null=True)

    class DeliveryChoices(models.Choices):
        STANDARD = 'standard'
        # PRIME = 'prime'
    delivery    = models.CharField(max_length=50, choices=DeliveryChoices.choices, default=DeliveryChoices.STANDARD)

    created_on  = models.DateField(auto_now_add=True)

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

class LookBook(models.Model):
    name    = models.CharField(max_length=70)
    products = models.ManyToManyField(Product)
    create_on = models.DateField(default=utils.timezone.now)

    def __str__(self):
        return self.name


@receiver(post_save, sender=Product)
def create_slug(instance, sender, created, **kwargs):
    if created:
        if instance.name:
            instance.slug = utilities.create_product_slug(instance.name)
            instance.save()

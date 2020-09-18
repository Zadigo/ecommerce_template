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


class Collection(models.Model):
    """
    Represents a collection of products
    """
    name      = models.CharField(max_length=50)

    class GenderChoices(models.Choices):
        FEMME = 'femme'
        HOMME = 'homme'
    gender = models.CharField(max_length=50, choices=GenderChoices.choices, default=GenderChoices.FEMME)
    
    view_name   = models.CharField(max_length=50)
    image        = models.FileField(upload_to='collections', blank=True, null=True)
    presentation_text = models.TextField(max_length=300, blank=True, null=True)
    google_description = models.CharField(max_length=160, blank=True, null=True)
    show_presentation  = models.BooleanField(default=False)

    automatic = models.BooleanField(default=False)
    criterion     = models.ManyToManyField(AutomaticCollectionCriteria, blank=True)

    objects = models.Manager()
    collection_manager = managers.CollectionManager.as_manager()

    class Meta:
        ordering = ['-pk']

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
    """
    name          = models.CharField(max_length=50, blank=True, null=True)
    reference   = models.CharField(max_length=30, default=utilities.create_product_reference())
    class GenderChoices(models.Choices):
        FEMME = 'femme'
        HOMME = 'homme'
    gender = models.CharField(max_length=50, choices=GenderChoices.choices, default=GenderChoices.FEMME)

    images          = models.ManyToManyField(Image)
    collection      = models.ForeignKey(Collection, on_delete=models.CASCADE, blank=True, null=True)
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
    google_category = models.CharField(max_length=5, choices=GoogleProductCategory.choices, default=GoogleProductCategory.TOPS)

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
        images = self.images.all()
        main_images = images.filter(main_image=True)
        if main_images.exists():
            image = main_images.first()
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
        return reverse('shop:product', args=['femme', collection_name, self.pk, self.slug])

    def get_preview_url(self):
        return reverse('shop:preview', args=[self.pk, self.slug])
    
    def get_private_url(self):
        return reverse('shop:private', args=[self.pk, self.slug])

    def get_collection_url(self):
        return reverse('shop:collection', args=[self.gender, self.collection.view_name])
    
    # @cached_property
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


class LookBook(models.Model):
    """
    Lookbook for the store
    """
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

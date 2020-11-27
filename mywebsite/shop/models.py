import datetime
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.shortcuts import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from shop import choices, managers, utilities, validators

MYUSER = get_user_model()

class Image(models.Model):
    """
    Represents an image for a given product
    """
    name    = models.CharField(max_length=50)
    variant = models.CharField(max_length=30, default='Noir')
    url = models.ImageField(
        verbose_name='Product image', 
        upload_to=utilities.images_directory_path,
        blank=True, 
        null=True
    )
    image_thumbnail = ImageSpecField(
        source='url', 
        processors=ResizeToFill(800), 
        format='JPEG', 
        options={'quality': 50}
    )
    web_url     = models.URLField(blank=True, null=True)
    main_image  = models.BooleanField(default=False, help_text='Indicates if this is the main image for the product')
    created_on = models.DateField(auto_now=True)

    objects = models.Manager()
 
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['url']),
        ]

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse('manage_image', args=[self.pk])

    def get_image(self):
        if not self.url:
            return self.web_url
        return self.url


class AutomaticCollectionCriteria(models.Model):
    """
    Stores conditions of classifying products automatically
    under a specific collection
    """
    reference = models.CharField(max_length=50, default=utilities.create_reference())

    condition    = models.CharField(
        max_length=50, 
        choices=choices.SecondConditionsChoices.choices, 
        default=choices.SecondConditionsChoices.IS_EQUAL_TO
    )
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
    gender = models.CharField(
        max_length=50, 
        choices=choices.GenderChoices.choices, 
        default=choices.GenderChoices.WOMEN
    )
    
    view_name   = models.CharField(max_length=50)
    image        = models.FileField(upload_to='collections', blank=True, null=True)
    presentation_text = models.TextField(max_length=300, blank=True, null=True)
    google_description = models.CharField(max_length=160, blank=True, null=True)
    show_presentation  = models.BooleanField(default=False)

    automatic = models.BooleanField(default=False)
    criterion     = models.ManyToManyField(AutomaticCollectionCriteria, blank=True)

    show_in_menu = models.BooleanField(default=False)

    objects = models.Manager()
    collection_manager = managers.CollectionManager.as_manager()

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return self.name

    def clean(self):
        if self.name:
            self.view_name = self.name.replace(' ', '').lower()

    @property
    def lower_case_gender(self):
        return self.gender.lower()

    def get_absolute_url(self):
        return reverse('shop:collection', args=[self.lower_case_gender, self.view_name])

    def get_shop_gender_url(self):
        return reverse('shop:gender', args=[self.lower_case_gender])


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
    gender = models.CharField(
        max_length=50, 
        choices=choices.GenderChoices.choices, 
        default=choices.GenderChoices.WOMEN
    )

    images = models.ManyToManyField(Image)
    video = models.FileField(
        upload_to=utilities.videos_directory_path,
        blank=True, 
        null=True
    )
    collection      = models.ForeignKey(Collection, on_delete=models.CASCADE, blank=True, null=True)
    variant        = models.ManyToManyField(Variant, blank=True)

    description   = models.TextField(max_length=280, blank=True, null=True)
    description_html = models.TextField(max_length=800, blank=True, null=True)
    description_objects  = models.TextField(max_length=800, blank=True, null=True)

    price_pre_tax    = models.DecimalField(max_digits=5, decimal_places=2)
    discount_pct    = models.IntegerField(default=10, blank=True)
    discounted_price   = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    price_valid_until = models.DateField(default=utilities.add_to_current_date(d=30))
    quantity        = models.IntegerField(default=0, blank=True)

    sku      = models.CharField(max_length=50, blank=True, null=True, help_text='ex. BCLOGO-GRIS-SMA')

    google_category = models.CharField(
        max_length=5, 
        choices=choices.GoogleProductCategory.choices, 
        default=choices.GoogleProductCategory.TOPS
    )

    in_stock     = models.BooleanField(default=True)
    discounted  = models.BooleanField(default=False)
    our_favorite    = models.BooleanField(default=False)
    active      = models.BooleanField(default=False)
    private     = models.BooleanField(default=False, help_text='Product is on accessible by sharing the direct link')

    slug        = models.SlugField()
    
    monitor_quantity = models.BooleanField(default=False)
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
                calculate_discount(self.price_pre_tax, self.discount_pct)
        
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
            return image.url.url
        else:
            try:
                # In case no main image was marked
                # then try to return the first image -;
                # However, there can be an exceptional
                # case where the product has no image
                # and in which case, we have to protect
                # against a NoneType error
                return images.first().url.url
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

    @property
    def lower_case_gender(self):
        return self.gender.lower()

    def get_absolute_url(self):
        return reverse('shop:product', args=[
            self.lower_case_gender, self.collection.view_name, self.pk, self.slug
        ])

    def get_preview_url(self):
        return reverse('shop:preview', args=[self.pk, self.slug])
    
    def get_private_url(self):
        return reverse('shop:private', args=[self.pk, self.slug])

    def get_collection_url(self):
        # return reverse('shop:collection', args=[self.gender, self.collection.view_name])
        return self.collection.get_absolute_url()
    
    def get_product_images(self):
        return self.images.all()

    def get_shop_gender_url(self):
        return reverse('shop:gender', args=[self.lower_case_gender])

    def get_price(self):
        """Chooses between the pre tax price and the
        discounted price if the product is discounted
        """
        if self.discounted_price is None:
            return self.price_pre_tax
        elif self.discounted_price > 0 and self.discounted:
            return self.discounted_price
        else:
            return self.price_pre_tax


class Like(models.Model):
    """
    Represents products that were liked by customers
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    user    = models.ForeignKey(MYUSER, on_delete=models.CASCADE, blank=True, null=True)

    objects = models.Manager()

    def __str__(self):
        return self.product.name


@receiver(post_save, sender=Product)
def create_slug(instance, sender, created, **kwargs):
    if created:
        if instance.name:
            instance.slug = utilities.create_product_slug(instance.name)
            instance.save()


@receiver(post_delete, sender=Image)
def delete_image(sender, instance, **kwargs):
    is_s3_backend = False
    try:
        is_s3_backend = settings.USE_S3
    except:
        pass

    if not is_s3_backend:
        if instance.url:
            if os.path.isfile(instance.url.path):
                os.remove(instance.url.path)
    else:
        instance.url.delete(save=False)


# @receiver(pre_delete, sender=Product)
def delete_images(sender, instance, **kwargs):
    images = instance.images.all()
    for image in images:
        if image.url:
            if os.path.isfile(image.url.path):
                os.remove(image.url.path)


@receiver(pre_save, sender=Image)
def delete_image_on_update(sender, instance, **kwargs):
    is_s3_backend = False
    try:
        is_s3_backend = settings.USE_S3
    except:
        pass

    if not is_s3_backend:
        if instance.pk:
            try: 
                old_image = Image.objects.get(pk=instance.pk)
            except:
                return False
            else:
                new_image = instance.url
                if old_image and old_image != new_image:
                    if os.path.isfile(old_image.url.path):
                        os.remove(old_image.url.path)
    else:
        instance.url.delete(save=False)

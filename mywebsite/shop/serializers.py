from rest_framework import fields
from rest_framework.serializers import Serializer

from shop import models


class VariantSerializer(Serializer):
    pk = fields.IntegerField()
    name = fields.CharField()
    verbose_name = fields.CharField()
    in_stock = fields.BooleanField()
    active = fields.BooleanField()


class ImageSerializer(Serializer):
    pk      = fields.IntegerField()
    name    = fields.CharField()
    url = fields.URLField()
    variant = fields.CharField()
    main_image = fields.BooleanField()


class CollectionSerializer(Serializer):
    name      = fields.CharField()


class ProductSerializer(Serializer):
    pk      = fields.IntegerField()
    reference  = fields.CharField()
    collection  = CollectionSerializer()
    images      = ImageSerializer(many=True)
    variant     = VariantSerializer(many=True)
    name          = fields.CharField()
    in_stock       = fields.BooleanField()
    our_favorite = fields.BooleanField()
    is_discounted = fields.BooleanField()
    price_ht = fields.DecimalField(5, 2)
    discounted_price = fields.DecimalField(5, 2)
    slug        = fields.SlugField()


class AnonymousCartSerializer(Serializer):
    pass


class CartSerializer(Serializer):
    pass


class DiscountSerializer(Serializer):
    product  = ProductSerializer(many=True)
    collection  = CollectionSerializer(many=True)
    code      = fields.CharField()
    value   = fields.IntegerField()


class SimpleProductSerializer(Serializer):
    pk  = fields.IntegerField()

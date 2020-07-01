from rest_framework import fields
from rest_framework.serializers import Serializer

from shop import models


class ClotheSizeSerializer(Serializer):
    name = fields.CharField()
    

class ImageSerializer(Serializer):
    pk = fields.IntegerField()
    name = fields.CharField()
    url = fields.URLField()
    variant = fields.CharField()
    main_image = fields.BooleanField()


class CollectionSerializer(Serializer):
    name = fields.CharField()


class ProductSerializer(Serializer):
    collection = CollectionSerializer()
    images = ImageSerializer(many=True)
    clothe_size = ClotheSizeSerializer(many=True)
    name = fields.CharField()
    in_stock = fields.BooleanField()
    slug = fields.SlugField()


class AnonymousCartSerializer(Serializer):
    pass


class CartSerializer(Serializer):
    pass


class DiscountSerializer(Serializer):
    product = ProductSerializer(many=True)
    collection = CollectionSerializer(many=True)
    code = fields.CharField()
    value = fields.IntegerField()

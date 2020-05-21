from rest_framework.serializers import Serializer
from rest_framework import fields
from shop import models

class ClotheSizeSerializer(Serializer):
    name = fields.CharField()
    centimeters = fields.IntegerField()

class ImageSerializer(Serializer):
    name    = fields.CharField()
    url     = fields.URLField()
    variant = fields.CharField()

class CollectionSerializer(Serializer):
    name      = fields.CharField()

class ProductSerializer(Serializer):
    collection  = CollectionSerializer()
    images      = ImageSerializer(many=True)
    clothe_size = ClotheSizeSerializer(many=True)
    name          = fields.CharField()
    slug        = fields.SlugField()

class AnonymousCartSerializer(Serializer):
    pass

class CartSerializer(Serializer):
    pass

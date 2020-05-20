from rest_framework.serializers import Serializer
from rest_framework import fields
from shop import models


class ImageSerializer(Serializer):
    name    = fields.CharField()
    # url     = fields.URLField()


class CollectionSerializer(Serializer):
    name      = fields.CharField()

class ProductSerializer(Serializer):
    collection  = CollectionSerializer()
    images      = ImageSerializer()
    name          = fields.CharField()
    slug        = fields.SlugField()

class AnonymousCartSerializer(Serializer):
    pass

class CartSerializer(Serializer):
    pass

from rest_framework.serializers import Serializer
from rest_framework import fields
from shop import models

class ClotheSizeSerializer(Serializer):
    name = fields.CharField()
    chest_circumference = fields.IntegerField()
    waist_hip_circumference = fields.IntegerField()

class ImageSerializer(Serializer):
    pk      = fields.IntegerField()
    name    = fields.CharField()
    url     = fields.URLField()
    variant = fields.CharField()
    main_image = fields.BooleanField()

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

class PromotionalCodeSerializer(Serializer):
    product  = ProductSerializer(many=True)
    collection  = CollectionSerializer(many=True)
    code      = fields.CharField()
    value   = fields.IntegerField()

from rest_framework import fields
from rest_framework.serializers import Serializer


class AnonymousCartSerializer(Serializer):
    pass


class CartSerializer(Serializer):
    pass


class DiscountSerializer(Serializer):
    product  = ProductSerializer(many=True)
    collection  = CollectionSerializer(many=True)
    code      = fields.CharField()
    value   = fields.IntegerField()

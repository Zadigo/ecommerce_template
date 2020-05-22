from django.contrib import admin

from shop import models


@admin.register(models.Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['name']
    # search_fields = ['name']
    # filter_horizontal = []
    # filter_vertical = []

@admin.register(models.ProductCollection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name']
    # search_fields = ['name']

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'collection', 'price_ht']
    # search_fields = []
    # filter_horizontal = []
    # filter_vertical = []

@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['cart_id', 'get_product_total']
    # search_fields = ['product__name']
    # filter_horizontal = []
    # filter_vertical = []

@admin.register(models.CustomerOrder)
class CustomerOrderAdmin(admin.ModelAdmin):
    list_display = ['cart']
    # search_fields = ['anonymous_cart', 'cart']
    # filter_horizontal = []
    # filter_vertical = []

@admin.register(models.Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['customer_order']
    # search_fields = []
    # filter_horizontal = []
    # filter_vertical = []
    
@admin.register(models.PromotionalCode)
class PromotionalCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'is_valid']
    # search_fields = []
    # filter_horizontal = []
    # filter_vertical = []

@admin.register(models.ClotheSize)
class ClotheSizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'verbose_name', 'centimeters']
    # search_fields = []
    # filter_horizontal = []
    # filter_vertical = []

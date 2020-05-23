from django.contrib import admin

from shop import models


@admin.register(models.Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(models.ProductCollection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name']
    # search_fields = ['name']

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'collection', 'get_price', 'is_discounted']
    search_fields = ['name', 'collection__name']
    filter_horizontal = ['images', 'clothe_size']
    sortable_by = ['name']
    date_hierarchy = 'created_on'
    prepopulated_fields = {'slug': ['name']}

@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['cart_id', 'get_product_total']
    search_fields = ['product__name']

@admin.register(models.CustomerOrder)
class CustomerOrderAdmin(admin.ModelAdmin):
    list_display = ['cart', 'payment']
    search_fields = ['reference', 'transaction', 'cart__product__name']
    date_hierarchy = 'created_on'
    sortable_by = ['payment']

@admin.register(models.Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['customer_order']
    search_fields = ['customer_code']
    # date_hierarchy = 'created_on'
    
@admin.register(models.PromotionalCode)
class PromotionalCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'is_valid']
    search_fields = ['code']

@admin.register(models.ClotheSize)
class ClotheSizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'verbose_name', 'centimeters']
    search_fields = ['name']
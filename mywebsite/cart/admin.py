from django.contrib import admin
from cart import models

@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['cart_id', 'get_product_total', 'paid_for']
    search_fields = ['product__name']


@admin.register(models.CustomerOrder)
class CustomerOrderAdmin(admin.ModelAdmin):
    list_display = ['reference', 'transaction', 'payment', 'accepted', 'completed']
    search_fields = ['reference', 'transaction']
    date_hierarchy = 'created_on'
    sortable_by = ['payment']
    filter_horizontal = ['cart']
    list_per_page = 20


@admin.register(models.Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['customer_order']
    search_fields = ['customer_code']
    # date_hierarchy = 'created_on'


@admin.register(models.Review)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = ['customer_order', 'rating']
    search_fields = ['product']

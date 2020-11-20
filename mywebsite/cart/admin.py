from django.contrib import admin
from cart import models

@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['cart_id', 'get_product_total', 'paid_for', 'created_on']
    search_fields = ['product__name']


@admin.register(models.CustomerOrder)
class CustomerOrderAdmin(admin.ModelAdmin):
    list_display = ['reference', 'transaction', 'payment', 'accepted', 'shipped', 'refund', 'created_on']
    search_fields = ['reference', 'transaction']
    date_hierarchy = 'created_on'
    sortable_by = ['payment', 'created_on']
    filter_horizontal = ['cart']
    list_per_page = 20
    actions = ['mark_accepted', 'mark_shipped']

    def mark_accepted(self, queryset):
        queryset.update(accepted=True)
        return queryset
    
    def mark_shipped(self, queryset):
        queryset.update(shipped=True)
        return queryset


@admin.register(models.Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['customer_order']
    search_fields = ['customer_code']
    date_hierarchy = 'created_on'

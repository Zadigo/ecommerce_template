from django.contrib import admin
from discounts.models import Discount

@admin.register(Discount)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'value', 'value_type', 'start_date', 'end_date']
    search_fields = ['code', 'value_type',
                     'product__name', 'product__reference']
    fieldsets = [
        ['General', {'fields': ['code', 'value', 'value_type']}],
        ['Discount type', {'fields': [
            'product', 'collection', 'on_entire_order']}],
        ['Purchase', {'fields': ['minimum_purchase', 'minimum_quantity']}],
        ['Usage', {'fields': ['usage_limit']}],
        ['State', {'fields': ['active', 'start_date', 'end_date']}]
    ]

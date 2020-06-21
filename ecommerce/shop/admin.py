from django.contrib import admin

from shop import models


@admin.register(models.Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['name', 'variant']
    search_fields = ['name', 'variant']
    list_per_page = 10

@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'gender', 'view_name']
    search_fields = ['name', 'view_name']

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'collection', 'gender', \
                        'get_price', 'is_discounted', 'active']
    search_fields = ['name', 'collection__name']
    filter_horizontal = ['images', 'clothe_size']
    sortable_by = ['name']
    date_hierarchy = 'created_on'
    list_filter = ['active', 'discounted', 'our_favorite']
    list_per_page = 10
    prepopulated_fields = {'slug': ['name']}

@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['cart_id', 'get_product_total']
    search_fields = ['product__name']

@admin.register(models.CustomerOrder)
class CustomerOrderAdmin(admin.ModelAdmin):
    list_display = ['reference', 'transaction', 'payment']
    search_fields = ['reference', 'transaction']
    date_hierarchy = 'created_on'
    sortable_by = ['payment']

@admin.register(models.Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['customer_order']
    search_fields = ['customer_code']
    # date_hierarchy = 'created_on'
    
@admin.register(models.Discount)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'value', 'value_type', 'start_date', 'end_date']
    search_fields = ['code', 'value_type', 'product__name', 'product__reference']
    fieldsets = [
        ['General', {'fields': ['code', 'value', 'value_type']}],
        ['Discount type', {'fields': ['product', 'collection', 'on_entire_order']}],
        ['Purchase', {'fields': ['minimum_purchase', 'minimum_quantity']}],
        ['Usage', {'fields': ['usage_limit']}],
        ['State', {'fields': ['active', 'start_date', 'end_date']}]
    ]

@admin.register(models.ClotheSize)
class ClotheSizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'verbose_name']
    search_fields = ['name']

@admin.register(models.Review)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = ['product', 'rating']
    search_fields = ['product']

@admin.register(models.Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['store_name', 'store_contact_email', 'legal_name']
    fieldsets = [
        ['General', {'fields': ['store_name', 'legal_name', 'store_industry', 'currency', 'tax_rate']}],
        ['Contact', {'fields': ['telephone', 'address', 'city', 'zip_code', 'store_contact_email', 'customer_care_email']}],
        ['Payment', {'fields': ['enable_apple_pay', 'enable_google_pay']}],
        ['Accounts', {'fields': ['accounts_disabled', 'accounts_optional']}],
        ['Banners', {'fields': ['mobile_banner', 'nav_banner']}],
        ['Archiving', {'fields': ['automatic_archive']}],
        ['Analytics', {'fields': ['google_analytics_tag', 'google_tag_manager_tag', 'google_optimize_tag', 'google_ads_tag', 'facebook_pixels_tag', 'mailchimp_tag']}],
        ['Coupons', {'fields': ['allow_coupons']}],
    ]

@admin.register(models.AutomaticCollection)
class AutomaticCollectionAdmin(admin.ModelAdmin):
    list_display = []
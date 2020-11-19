from django.contrib import admin

from shop import models


@admin.register(models.Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['name', 'variant']
    search_fields = ['name', 'variant']
    list_per_page = 10

    def delete_queryset(self, request, queryset):
        for image in queryset:
            image.delete()


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'gender', 'view_name']
    search_fields = ['name', 'view_name']


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'collection', 'gender', \
                        'get_price', 'is_discounted', 'active']
    search_fields = ['name', 'collection__name']
    filter_horizontal = ['images', 'variant']
    sortable_by = ['name']
    date_hierarchy = 'created_on'
    list_filter = ['active', 'discounted', 'our_favorite']
    list_per_page = 10
    prepopulated_fields = {'slug': ['name']}


@admin.register(models.Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ['name', 'verbose_name', 'in_stock', 'active']
    search_fields = ['name']
    list_per_page = 10


@admin.register(models.Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['product', 'user']
    search_fields = ['product', 'user']
    list_per_page = 10

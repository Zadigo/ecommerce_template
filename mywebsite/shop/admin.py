import os

from django.conf import settings
from django.contrib import admin
from imagekit.admin import AdminThumbnail

from shop import models


@admin.register(models.Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['name', 'variant', 'main_image']
    # admin_thumbnail = AdminThumbnail(image_field='image_thumbnail')
    search_fields = ['name', 'variant']
    list_per_page = 10
    actions = ['mark_as_main_image', 'unmark_as_main_image']
    sortable_by = ['name', 'variant']
    list_filter = ['main_image']
    date_hierarchy = 'created_on'

    admin_thumbnail = AdminThumbnail(image_field='image_thumbnail')

    def delete_queryset(self, request, queryset):
        for image in queryset:
            image.delete()

    def mark_as_main_image(self, request, queryset):
        queryset.update(main_image=True)

    def unmark_as_main_image(self, request, queryset):
        queryset.update(main_image=False)

    def clear_unlinked_images(self, request, queryset):
        """
        Delete images that are not used by at least
        one product. This function should be used mainly
        to purge the media directory for useless images
        """
        try:
            is_s3_backend = settings.USE_S3
        except:
            pass
        else:
            unlinked_images = queryset.filter(product__id=None)
            if unlinked_images.exists():
                for unlinked_image in unlinked_images:
                    if is_s3_backend:
                        unlinked_image.url.delete(commit=False)
                    else:
                        if os.path.isfile(unlinked_image.url.path):
                            os.remove(unlinked_image.url.path)


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
    actions = ['duplicate', 'activate', 'deactivate',
               'mark_as_favorite', 'mark_as_private']
    fieldsets = [
        ['General', {'fields': ['name', 'reference', 'description', 'description_html', 'description_objects']}],
        ['Media', {'fields': ['images', 'video']}],
        ['Classification', {'fields': ['gender', 'collection', 'google_category', 'sku']}],
        ['Variants', {'fields': ['variant']}],
        ['Pricing', {'fields': ['price_pre_tax', 'price_valid_until']}],
        ['Discounts', {'fields': ['discount_pct', 'discounted_price', 'discounted']}],
        ['Quantity', {'fields': ['quantity', 'monitor_quantity', 'in_stock']}],
        ['Other', {'fields': ['slug', 'our_favorite', 'to_be_published_on', 'private', 'active']}]
    ]
    # read_only_fields = ['description_html', 'description_objects']

    # class Media:
    #     js = ['js/admin_quill.js']

    def mark_as_favorite(self, requestn, queryset):
        queryset.update(our_favorite=True)
        
    def mark_as_private(self, requestn, queryset):
        queryset.update(private=True)

    def activate(self, request, queryset):
        queryset.update(active=True)

    def deactivate(self, request, queryset):
        queryset.update(active=False)

    def duplicate(self, request, queryset):
        new_products = []
        images_queryset = []
        for index, product in enumerate(queryset):
            collection = models.Collection.objects.get(name=product.collection.name)
            images_queryset.append(product.images.all())
            new_products.append(
                models.Product(
                    name=f'New Product {index}',
                    collection=collection,
                    description=product.description,
                    description_html=product.description_html,
                    price_pre_tax=product.price_pre_tax,
                    discount_pct=product.discount_pct,
                    discounted_price=product.discounted_price,
                    price_valid_until=product.price_valid_until,
                    in_stock=product.in_stock,
                    discounted=product.discounted,
                    slug=f'new-product-{index}'
                )
            )
        
        new_products = models.Product.objects.bulk_create(new_products)
        for index, product in enumerate(new_products):
            product.images.set(images_queryset[index])


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

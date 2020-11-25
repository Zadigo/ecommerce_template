from django.contrib import admin
from store import models

@admin.register(models.Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'active']
    search_fields = ['name']


@admin.register(models.Analytic)
class AnalyticsAdmin(admin.ModelAdmin):
    list_display = ['google_analytics']
    search_fields = ['google_analytics']
    list_per_page = 15


@admin.register(models.PaymentOption)
class PaymentOptionsAdmin(admin.ModelAdmin):
    list_display = ['store_currency']
    search_fields = ['store_currency']


@admin.register(models.Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'email']
    search_fields = ['name', 'country', 'email', 'store__name', 'store__user', 'store__legal_name']
    list_per_page = 15
    actions = ['archive', 'unarchive']

    def archive(self, request, queryset):
        queryset.update(archive=True)

    def unarchive(self, request, queryset):
        queryset.update(archive=True)

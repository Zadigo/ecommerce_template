from django.contrib import admin

from lookbook.models import LookBook


@admin.register(LookBook)
class LookbookAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_on']
    search_fields = ['products__name', 'products__reference']
    filter_horizontal = ['products']
    date_hierarchy = 'created_on'
    list_per_page = 10

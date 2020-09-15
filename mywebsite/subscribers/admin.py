from django.contrib import admin

from subscribers import models


@admin.register(models.EmailSubscriber)
class SubscribedUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'created_on']
    date_hierarchy = 'created_on'
    list_filter = ['created_on']
    list_per_page = 30

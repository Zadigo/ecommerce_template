from django.contrib import admin
from dashboard import models

@admin.register(models.DashboardSetting)
class DashboardSettingsAdmin(admin.ModelAdmin):
    list_display = ['myuser', 'dark_mode']

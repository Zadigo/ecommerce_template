from django.contrib import admin
from analytics.models import Analytic


@admin.register(Analytic)
class AnalyticAdmin(admin.ModelAdmin):
    list_display = ['reference', 'modified_on']

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import fields, signals
from django.dispatch import receiver

from dashboard import managers

USER = get_user_model()

class DashboardSetting(models.Model):
    user    = models.OneToOneField(USER, on_delete=models.CASCADE)
    dark_mode = fields.BooleanField(default=False)

    objects = models.Manager()
    dashboard_manager = managers.DashboardManager.as_manager()

    def __str__(self):
        return self.dark_mode

@receiver(signals.post_save, sender=USER)
def create_user_dashboard(instance, sender, created, **kwargs):
    if created:
        DashboardSetting.objects.create(user=instance)
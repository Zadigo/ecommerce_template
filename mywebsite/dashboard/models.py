from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import fields, signals
from django.dispatch import receiver

MYUSER = get_user_model()

class DashboardSetting(models.Model):
    myuser    = models.OneToOneField(MYUSER, on_delete=models.CASCADE)
    dark_mode = fields.BooleanField(default=False)
    
    objects = models.Manager()

    def __str__(self):
        return self.myuser.email

@receiver(signals.post_save, sender=MYUSER)
def create_user_dashboard(instance, sender, created, **kwargs):
    if created:
        DashboardSetting.objects.create(myuser=instance)

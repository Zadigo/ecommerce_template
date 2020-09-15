from django.db import models
from subscribers import mailchimp

class AbstractSubscriber(models.Model):
    email = models.EmailField(blank=True, null=True)
    created_on = models.DateField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        abstract = True

    def __str__(self):
        return self.email

    def clean(self):
        if self.email is not None:
            klass = mailchimp.MailChimp()


class EmailSubscriber(AbstractSubscriber):
    """People who subscribed to the website"""
    pass

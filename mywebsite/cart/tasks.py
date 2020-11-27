import time

from celery import Celery, beat, shared_task
from celery.schedules import crontab
from django.core.mail import send_mail
from django.db import transaction

from cart import emailing, models


@shared_task
def purchase_complete_email(request, to_email, **data):
    """
    Send an email to a customer after
    purchase
    """
    time.sleep(3)
    send_mail(
        'Testing celery',
        'Hey we are just testing',
        'contact.mywebsite@gmail.com',
        ['wiyeni8357@icanav.net']
    )
    return True


@shared_task
def clean_carts():
    """
    Delete carts that are older than x days
    """
    carts = models.Cart.cart_manager.over_thirtee_days()
    if carts.exists():
        carts.delete()
    return list(carts.all().values('id'))


@shared_task
def automatic_archive():
    """
    Archive orders on a periodic basis
    when they have been marked as fulfilled
    """
    pass

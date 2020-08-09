import time

from celery import Celery, beat, shared_task
from celery.schedules import crontab
from django.core.mail import send_mail
from django.db import transaction

from shop import models


@shared_task
def purchase_complete_email(to_customer=None):
    """
    Send an email to a customer after
    purchase
    """
    print('Sending mail')
    time.sleep(3)
    send_mail(
        'Testing celery',
        'Hey we are just testing',
        'contact.mywebsite@gmail.com',
        ['wiyeni8357@icanav.net']
    )
    return True


@shared_task
def publish_product():
    """
    Publish products marked as 'to be published'
    in a future date as published
    """
    # products = models.Product.product_manager.to_be_published_today()
    # if products.exists():
    #     products.update(active=True)
    print('Product was published')


@shared_task
def add_to_collection():
    """
    Add a product to a collection dynamically
    after creation based on certain conditions
    """
    pass


@shared_task
def product_is_out_of_stock():
    """
    Put products which quantity has reached
    zero as out of stock
    """
    pass


@shared_task
def clean_carts():
    """
    Delete carts that are older than x days
    """
    pass


@shared_task
def automatic_archive():
    """
    Archive orders on a periodic basis
    when they have been marked as fulfilled
    """
    pass

def delete_carts_from_over_thirtee_days():
    carts = models.Cart.cart_manager.over_thirtee_days()
    if carts.exists():
        try:
            with transaction.atomic():
                carts.delete()
        except:
            return False
        else:
            return 'Transaction successful'
    return False

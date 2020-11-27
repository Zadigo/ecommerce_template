from __future__ import absolute_import, unicode_literals

import time

from celery import Celery, beat, shared_task
from celery.schedules import crontab
from django.core.mail import send_mail
from django.db import transaction

from shop import models


@shared_task
def publish_product():
    """
    Publish products marked as 'to be published'
    in a future date as published
    """
    products = models.Product.product_manager.to_be_published_today()
    if products.exists():
        products.update(active=True)
    return products.count()


@shared_task
def add_to_collection():
    """
    Add a product to a collection dynamically
    after creation based on certain conditions
    """
    return [1, 4, 5, 2]


@shared_task
def product_is_out_of_stock():
    """
    Put products which quantity has reached
    zero as out of stock
    """
    # queryset = models.Product.product_manager.out_of_stock()
    # if queryset.exists():
    #       queryset.update(in_stock=False)
    # return queryset.values('id', 'reference')
    pass

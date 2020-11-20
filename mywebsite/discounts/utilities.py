import random
import string

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.apps import apps


def get_product_model():
    """
    Get the product model for the project
    """
    try:
        product_model = settings.PRODUCT_MODEL
    except:
        raise ImproperlyConfigured(
            "You should configure the Product model to use in settings for the discounts application")
    else:
        return apps.get_model(product_model, require_ready=False)


def get_product_collection_model():
    """
    Get the product collection model for the project
    """
    try:
        model = settings.PRODUCT_COLLECTION_MODEL
    except:
        raise ImproperlyConfigured(
            "You should configure the Product model to use in settings for the discounts application")
    else:
        return apps.get_model(model, require_ready=False)


def create_discount_code():
    n = random.randrange(1000, 9000)
    s = random.choice(string.ascii_uppercase)
    return f'NAW{n}{s}'

import datetime
import hashlib
import random
import secrets
import string
import uuid

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _


def get_product_model():
    """
    Get the product model for the project
    """
    try:
        product_model = settings.PRODUCT_MODEL
    except:
        raise ImproperlyConfigured("You should configure the Product model to use in settings for the cart application")
    else:
        return apps.get_model(product_model, require_ready=False)


def get_product_collection_model():
    """
    Get the product collection model for the project
    """
    try:
        model = settings.PRODUCT_COLLECTION_MODEL
    except:
        raise ImproperlyConfigured("You should configure the Product model to use in settings for the cart application")
    else:
        return apps.get_model(model, require_ready=False)


def get_discount_model():
    """
    Get the discount model for the project
    """

    try:
        model = settings.DISCOUNT_MODEL
    except:
        return None
    else:
        return apps.get_model(model, require_ready=False)


def create_discount_code():
    """
    Create a new discount code
    """

    n = random.randrange(1000, 9000)
    s = random.choice(string.ascii_uppercase)
    return f'NAW{n}{s}'


def create_cart_id(n=12):
    """Creates an iD for the Anonymous cart so that we can
    easily get all the items registered by an anonymous user
    in the cart.

    This iD is saved in the session and in the local storage.

    Description
    -----------

        2019_01_02_token
    """
    token = secrets.token_hex(n)
    date = datetime.datetime.now().date()
    return f'{date.year}_{date.month}_{date.day}_' + token


def create_transaction_token(n=1, salt='mywebsite'):
    """Create a payment token for Google enhanced ecommerce"""
    tokens = [secrets.token_hex(2) for _ in range(0, n)]
    # Append the salt that allows us to identify
    # if the payment method is a valid one
    tokens.append(hashlib.sha256(salt.encode('utf-8')).hexdigest())
    return '-'.join(tokens)


def calculate_vat(price, vat=20):
    """
    Calculates the tax on a product

    Formula
    -------
        price * (1 + (tax / 100))
    """
    return round(float(price) * (1 + (vat / 100)), 2)


def validate_payment_id(token, salt='mywebsite'):
    """Validate a payment ID"""
    parts = token.split('-')
    hashed_salt = hashlib.sha256(salt.encode('utf-8')).hexdigest()

    # The salt should always theoretically
    # be the last component of the array
    incoming_hashed_part = parts.pop(-1)

    truth_array = []

    # Compare incoming salt to salt
    if hashed_salt == incoming_hashed_part:
        truth_array.append(True)
    else:
        truth_array.append(False)

    # We should only have 5
    # parts in the array outside
    # of the salt
    if len(parts) == 5:
        truth_array.append(True)
    else:
        truth_array.append(False)

    # Each part should have a
    # maximum of 5 characters
    for part in parts:
        if len(part) != 4:
            truth_array.append(False)

    return all(truth_array)

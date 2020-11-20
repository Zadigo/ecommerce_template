from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_product_model():
    """
    Get the product model for the project
    """
    try:
        product_model = settings.PRODUCT_MODEL
    except:
        raise ImproperlyConfigured(
            "You should configure the Product model to use in settings for the store application")
    else:
        return apps.get_model(product_model, require_ready=False)

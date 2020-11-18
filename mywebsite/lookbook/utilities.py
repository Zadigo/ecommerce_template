from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_product_model():
    try:
        model = settings.PRODUCT_MODEL
    except:
        raise ImproperlyConfigured(
            "Please define PRODUCT_MODEL in the settings.py file"
        )
    else:
        return apps.get_model(model, require_ready=False)

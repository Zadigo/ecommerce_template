from django.apps import apps as project_apps
from django.conf import settings
from django.core import exceptions


def get_product_model():
    """Returns the main model to use for the
    dashboard
    """
    try:
        project_apps.get_model(settings.PRODUCT_MODEL, require_ready=False)
    except ValueError:
        raise exceptions.ImproperlyConfigured("PRODUCT_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise exceptions.ImproperlyConfigured((f"PRODUCT_MODEL refers to model '{settings.PRODUCT_MODEL}'" 
            "that has not been installed"))

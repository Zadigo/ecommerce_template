from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_user_profile_model():
    try:
        return django_apps.get_model(settings.AUTH_USER_PROFILE_MODEL, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured("AUTH_USER_PROFILE_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "AUTH_USER_PROFILE_MODEL refers to model '%s' that has not been installed" % settings.AUTH_USER_PROFILE_MODEL
        )

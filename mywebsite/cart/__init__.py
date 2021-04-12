from django.conf import settings
from importlib import import_module

def get_payment_backend():
    backend_string = getattr(settings, 'PAYMENT_BACKEND', None)
    module, obj_string = backend_string.split('.', maxsplit=1)
    module = import_module(module)
    backend = getattr(module, obj_string, None)
    return backend

import datetime
import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def generic_size_validator(size):
    """
    A simple validator for validating the sizes that
    are entered in the database
    """
    if not size:
        raise ValidationError("La taille n'est pas reconnue")
    is_match = re.match(r'^(\d+|[A-Za-z]{1,3})[A-Za-z]?$', size)
    if is_match:
        return size.upper()
    raise ValidationError("La taille n'est pas reconnue")

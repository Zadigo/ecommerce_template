import re
from django.utils.translation import gettext_lazy as _
from django.forms import ValidationError

def validate_analytics(tag):
    is_match = re.match(r'UA\-[0-9]{8}\-[0-9]{1}', tag)
    if is_match:
        return tag
    raise ValidationError(_("The Google Analytics tag is not valid (should be UA-XXXXXXXX-X)"))


def validate_tag_manager(tag):
    is_match = re.match(r'GTM\-[A-Z0-9]{7}', tag)
    if is_match:
        return tag
    raise ValidationError(_("The GTM tag is not valid (should be GTM-XXXXXXX)"))


def validate_optimize(tag):
    pass

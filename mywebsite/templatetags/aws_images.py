from urllib.parse import urljoin

from django import template
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

register = template.Library()

@register.simple_tag
def get_aws_prefix_url():
    try:
        return settings.MEDIA_URL
    except:
        raise ImproperlyConfigured(
            'You should specify a MEDIA_URL settings in order to us this tag')


@register.simple_tag
def build_aws_image_url(name):
    return f'{get_aws_prefix_url()}{name}'

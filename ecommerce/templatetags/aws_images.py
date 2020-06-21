"""Centralizes all the images present on the website
into one single area
"""

from django.conf import settings
from urllib.parse import urljoin
from django import template

register = template.Library()

@register.simple_tag
def create_aws_image_url(name):
    base = 'https://mybusinesses.s3.eu-west-3.amazonaws.com/nawoka_v2/hero/'
    # if not name.endswith('.jpg') \
    #         or not name.endswith('.jpeg'):
    #     return 'http://placeholder.com/800'
    return urljoin(base, name)
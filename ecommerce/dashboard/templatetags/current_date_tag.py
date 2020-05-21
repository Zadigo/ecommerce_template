from django import template
from django.shortcuts import reverse
import datetime

register = template.Library()

@register.simple_tag
def current_date():
    return {'current_date': str(datetime.datetime.date())}
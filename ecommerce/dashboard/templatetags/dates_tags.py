from django import template
import datetime

register = template.Library()

@register.filter
def in_cart_since(d):
    if not d:
        return "0 jours"
    current_date = datetime.datetime.now().date()
    difference = current_date - d
    return difference

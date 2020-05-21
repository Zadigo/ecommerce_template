from django import template

register = template.Library()


@register.filter
def price_to_text(price):
    return f'{price} €'
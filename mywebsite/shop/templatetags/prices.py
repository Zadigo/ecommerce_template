from django import template
from django.utils.html import mark_safe

register = template.Library()


@register.filter
def price_to_text(price):
    if price == 0 or price is None:
        return '0 €'
    return f'{price} €'


@register.filter
def number_to_percentage(number):
    return f'{number}%'


@register.filter
def discount_as_text(price):
    return f'-{price}%'

@register.filter
def discounted_price_as_text(price, currency):
    return mark_safe(f"""<strike>{price} €</strike>""")

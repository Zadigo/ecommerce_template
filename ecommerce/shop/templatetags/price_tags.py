from django import template

register = template.Library()


@register.filter
def price_to_text(price):
    return f'{price} €'

@register.filter
def number_to_percentage(number):
    return f'{number}%'
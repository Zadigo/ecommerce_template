from django.core.exceptions import ValidationError

def price_validator(price):
    if price < 0:
        raise ValidationError('Price should not be below 0')
    return price
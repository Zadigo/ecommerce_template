from django.core.exceptions import ValidationError
import datetime
import re

def price_validator(price):
    if price < 0:
        raise ValidationError('Price should not be below 0')
    return price

def quantity_validator(quantity):
    if quantity < 1 or quantity > 99:
        raise ValidationError('Quantity should be between 1 and 99')
    return quantity

def size_validator(size):
    """Checks if the size is within the accepted sizes
    and then substitutes the incoming size with the
    checked size"""
    sizes = ['XS', 'xs', 's', 'S', 
                    'm', 'M', 'l', 'L']
    if size is None:
        return None
    if size not in sizes:
        raise ValidationError('Size should be one of XS, S, M or L')
    else:
        return sizes[sizes.index(size)]
    return size

def cart_id_validator(cart_id):
    # 2020_5_21_1674a01adc8448ba05ddff09
    current_date = datetime.datetime.now().date()
    try:
        items = cart_id.split('_')
        token = items.pop(-1)
        dates = '-'.join(items)
    except:
        raise ValidationError('Could not find date in cart id')
    else:
        # Checks if the date is a valid element
        date_component = datetime.datetime.strptime(dates, '%Y-%m-%d')
        if all([date_component.year == current_date.year] and\
                    [date_component.month == current_date.month]):
            is_match = re.match(r'[a-z0-9]+', token)
            if is_match:
                return cart_id
            else:
                raise ValidationError('The token is not valid')
        else:
            raise ValidationError('The date is not a valid date')

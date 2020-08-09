import ast
import json
import re

from django.template import Library
from django.utils.html import mark_safe

from shop import models

register = Library()

def iterator(queryset):
    impressions = []
    for index, product in enumerate(queryset):
        impressions.append(
            dict(
                id = product.reference,
                name = product.name,
                price = str(product.get_price()),
                brand = 'Nawoka',
                category = product.collection.name,
                position = index,
                list = f'{product.collection.gender}/{product.collection.name}'
            )
        )
    # corrected = re.findall(r'(?<!\w)\'(?!\w)', str(impressions))
    # BUG: When we replace the quotes, the one within the 
    # string are also replaced creating a wrong dict
    # e.g. "Sac d"été" > "Sac d'été"
    return mark_safe(str(impressions).replace("\'", "\""))


@register.inclusion_tag('components/product/seo/multiple.html')
def impressions(products):
    return {'impressions': iterator(products)}

@register.inclusion_tag('components/product/seo/single.html')
def impression(products):
    return {'impressions': iterator(products)}

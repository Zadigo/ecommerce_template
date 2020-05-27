from django import template
import json

register = template.Library()

@register.simple_tag
def product_impressions(products):
    """Takes a queryset and returns a list
    of products"""
    product_impressions = []
    if not products:
        return product_impressions
    for index, product in enumerate(products):
        product_impressions.append({
            'id': product.id,
            'name': product.name,
            'price': str(product.get_price()),
            'brand': 'Nawoka',
            'category': product.collection.name,
            'position': index
        })
    a = f'''{product_impressions}'''.replace('\'', '\"')
    return a
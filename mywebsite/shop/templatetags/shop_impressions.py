import json
import re

from django.template import Library, Node
from django.template.base import token_kwargs
from django.template.exceptions import TemplateSyntaxError
from django.utils.safestring import mark_safe

register = Library()

def create_products_impressions(queryset, brand=None, metrics=None):
    """Create impressions for Google Analytics"""
    if queryset is None:
        return []
    impressions = []
    for index, item in enumerate(queryset):
        impressions.append(
            dict(
                id=item.reference,
                name=item.name,
                price=str(item.get_price()),
                brand=brand,
                category=item.collection.name,
                position=index,
                list=f'{item.collection.gender}/{item.collection.name}'
            )
        )
    return json.dumps(impressions)
    

class AnalyticsNode(Node):
    def __init__(self, extra_context=None):
        self.queryset = extra_context.get('queryset')
        self.brand = extra_context.get('brand')
        self.metrics = extra_context.get('metrics')

    def render(self, context):
        resolved_queryset = self.queryset.resolve(context)
        
        brand = None
        if self.brand is not None:
            brand = self.brand.resolve(context)
        impressions = create_products_impressions(
            resolved_queryset, brand=brand
        )
        return mark_safe(impressions) if impressions else ''


@register.tag
def impressions_for_shop(parser, token):
    """
    {% analytics_impressions queryset=queryset brand="Nawoka" metrics="a b c" %}
    """
    bits = token.split_contents()
    remaining_bits = bits[1:]
    extra_context = token_kwargs(remaining_bits, parser, support_legacy=False)
    if not extra_context:
        raise TemplateSyntaxError(
            f"'{bits[0]}' expects at least one key word variable"
        )
    return AnalyticsNode(extra_context=extra_context)

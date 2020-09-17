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
    return impressions


def create_impressions(queryset, brand=None, include_position=False):
    impressions = list(
        queryset.values(
            'reference',
            'name',
            'collection__name',
        )
    )
    fit_transformed = []
    fit_values = {
        'reference': 'id',
        'name': 'name',
        'collection__name': 'category',
        'true_price': 'price',
        'quantity': 'quantity',
        'brand': 'brand',
        'position': 'position',
        'color': 'variant',
        'total': 'metric1'
    }
    for index, impression in enumerate(impressions, start=1):
        new_values = {}
        impression['brand'] = brand
        if include_position:
            impression['position'] = index
        for key, value in impression.items():
            new_values[fit_values[key]] = str(value)
        fit_transformed.append(new_values)
    return json.dumps(fit_transformed)


class AnalyticsNode(Node):
    def __init__(self, extra_context=None):
        self.queryset = extra_context['queryset']
        self.brand = None
        self.metrics = None

        try:
            self.brand = extra_context['brand']
        except:
            pass

        try:
            self.metrics = extra_context['metrics']
        except:
            pass

    def render(self, context):
        from django.db.models import QuerySet

        resolved_queryset = self.queryset.resolve(context)
        
        brand = None
        if self.brand is not None:
            brand = self.brand.resolve(context)
        impressions = create_products_impressions(resolved_queryset, brand=brand)
        values = str(json.dumps(impressions))
        return mark_safe(values) if values else ''


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

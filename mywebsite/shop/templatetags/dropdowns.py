import random

from django import template
from django.core.cache import cache
from django.template import Node
from django.template.context import Context
from django.template.loader import get_template
from django.utils.html import format_html, format_html_join
from shop import models

register = template.Library()

SAMPLE_IMAGES = [
    'https://ae01.alicdn.com/kf/HTB1tAiYj9YTBKNjSZKbq6xJ8pXa4/CDJLFH-2019-t-femmes-mode-Crop-chemise-haute-couleur-unie-o-cou-manches-courtes-T-shirt.jpg'
]


def get_collections():
    collections = cache.get('collections', None)
    if collections is None:
        try:
            collections = models.Collection.objects.all()
        except Exception:
            raise
        else:
            cache.set('collections', collections, timeout=3600)
    return collections


@register.inclusion_tag('includes/navs/dropdowns/medium.html')
def collections_dropdown_block():
    collections = get_collections()
    collection = collections.first()
    context = {
        'has_collections': collections.exists(),
        'collections': collections
    }

    if collection:
        context['sample_collection'] = {
            'gender': collection.gender.lower(),
            'name': collection.name,
            'view_name': collection.view_name,
        }
        if not collection.image:
            product = collection.product_set.first()
            if product is not None:
                image = product.images.first()
                try:
                    context['sample_collection']['image'] = image.url
                except:
                    context['sample_collection']['image'] = SAMPLE_IMAGES[0]
                    context['sample_collection']['is_url'] = True
        else:
            context['sample_collection']['image'] = collection.image

    return context


@register.inclusion_tag('includes/product/cart.html')
def cart():
    context = {}
    context['cart'] = None
    return context


@register.simple_tag(takes_context=True)
def test_dropdown(context):
    collections = get_collections()
    collection = collections.first()

    context.push({
        'has_collections': collections.exists(),
        'collections': collections,
        'genders': set(collections.values_list('gender', flat=True))
    })
    if collection:
        details = {
            'gender': collection.gender,
            'name': collection.name,
            'view_name': collection.view_name,
            'url': collection.get_absolute_url()
        }
        if not collection.image or collection.image is None:
            product = collection.product_set.first()
            if product is not None:
                product_image = product.image
                try:
                    details['image'] = product_image.first().url
                except:
                    details['image'] = 'https://via.placeholder.com/500'
        else:
            details['image'] = collection.image.url
        context.push(sample_collection=details)

    t = get_template('includes/navs/dropdowns/_base.html')
    return t.render(context.flatten())

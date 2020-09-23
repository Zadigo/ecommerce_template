import random

from django import template
from django.core.cache import cache

from shop import models

register = template.Library()

SAMPLE_IMAGES = [
    'https://ae01.alicdn.com/kf/HTB1tAiYj9YTBKNjSZKbq6xJ8pXa4/CDJLFH-2019-t-femmes-mode-Crop-chemise-haute-couleur-unie-o-cou-manches-courtes-T-shirt.jpg'
]


def get_collections():
    collections = cache.get('collections', None)
    if not collections:
        collections = models.Collection.objects.all()
        cache.set('collections', collections, 60)
    return collections


@register.inclusion_tag('components/navs/dropdowns/medium.html')
def collections_dropdown_block():
    collections = get_collections()
    collection = collections.first()
    context = {
        'has_collections': collections.exists(),
        'collections': collections
    }

    if collection:
        context['sample_collection'] = {
            'gender': collection.gender,
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
        else:
            context['sample_collection']['image'] = collection.image
    return context



@register.inclusion_tag('components/product/cart.html')
def cart():
    context = {}
    context['cart'] = None
    return context

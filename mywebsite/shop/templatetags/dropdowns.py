from django import template
from django.core.cache import cache

from shop import models

register = template.Library()

collections = cache.get('collections', None)
if not collections:
    collections = models.ProductCollection.objects.all()
    cache.set('collections', collections, 60)

@register.inclusion_tag('project_components/navs/dropdowns/links.html')
def links():
    context = {
        'has_collections': collections.exists(),
        'collections': collections
    }
    return context


@register.inclusion_tag('project_components/navs/dropdowns/block.html')
def dropdown_block():
    context = {}
    if collections.exists():
        collection = collections.first()
        context.update({'block_gender': collection.gender})
        context.update({'block_name': collection.name})
        context.update({'block_view': collection.view_name})
        if not collection.image:
            product = collection.product_set.first()
            # Get the image of the first product
            # and use that
            image = product.images.first().url
            if image:
                context.update({'block_image': image})
            else:
                context.update({'block_image': 'https://ae01.alicdn.com/kf/HTB1tAiYj9YTBKNjSZKbq6xJ8pXa4/CDJLFH-2019-t-femmes-mode-Crop-chemise-haute-couleur-unie-o-cou-manches-courtes-T-shirt.jpg'})
        else:
            context.update({'block_image': collection.image})
    return context

from django import template
from django.core.cache import cache

from cart import models

register = template.Library()

@register.simple_tag
def number_of_products(request):
    cart_id = request.session.get('cart_id')
    if cart_id is None:
        return 0
    cart_count = cache.get('cache_count', None)
    if not cart_count:
        cart_count = models.Cart.cart_manager.number_of_products(cart_id, as_value=True)
        cache.set('cart_count', cart_count, 60)
    return cart_count


@register.inclusion_tag('components/product/cart.html')
def dropdown_cart(request):
    cart_id = request.session.get('cart_id')
    if cart_id:
        return {
            'cart': models.Cart.cart_manager.my_cart(cart_id)
        } 
    else:
        return {'cart': []}

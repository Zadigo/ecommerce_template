from django import template
from django.shortcuts import reverse

register = template.Library()


NAMESPACE = 'dashboard'

LINKS = [
    ['index', {'name': 'Dashboard', 'icon': 'fas fa-chart-pie'}],
    ['products:home', {'name': 'Produits', 'icon': 'fas fa-table'}],
    ['collections:home', {'name': 'Collections', 'icon': 'fas fa-table'}],
    ['customer_orders', {'name': 'Commandes', 'icon': 'fas fa-table'}],
    ['carts', {'name': 'Paniers', 'icon': 'fas fa-table'}],
    ['images:home', {'name': 'Images', 'icon': 'fas fa-images'}],
    ['coupons:home', {'name': 'Coupons', 'icon': 'fas fa-tag'}],
    # ['dashboard_users', {'name': 'Utilisateurs', 'icon': 'fas fa-user'}],
    # ['settings:home', {'name': 'Settings', 'icon': 'fas fa-cog'}],
]

@register.inclusion_tag('components/navs/sidenav_link.html')
def sidebar_links(request=None, for_admin=None):
    pass
    """Creates links for the sidenav"""
    if request:
        if not request.user.is_admin:
            pass
    for viewname, data in LINKS:
        data.update({'href': reverse(f'{NAMESPACE}:{viewname}')})
    return {'links': LINKS}

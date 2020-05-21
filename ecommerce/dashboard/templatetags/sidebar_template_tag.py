from django import template
from django.shortcuts import reverse

register = template.Library()

LINKS = [
    ['index', {'name': 'Dashboard', 'icon': 'fas fa-chart-pie'}],
    ['dashboard_products', {'name': 'Products', 'icon': 'fas fa-table'}]
]

@register.inclusion_tag('components/navs/links.html')
def create_links(*links):
    """Creates links for the sidenav"""
    reversed_links = []
    for index, link in enumerate(LINKS):
        if index == 0:
            link[1]['active'] = True
        reversed_links.append({'href': reverse(link[0]), 'attrs': link[1]})
    return {'links': reversed_links}
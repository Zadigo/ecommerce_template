from django.template import Library
from django.shortcuts import reverse


register = Library()


LINKS = [
    ['accounts:profile:home', {'name': 'Profil'}],
    ['accounts:profile:payment', {'name': 'Mode de paiement'}],
    ['accounts:profile:change_password', {'name': 'Mot de passe'}],
    ['accounts:profile:data', {'name': 'Mes données'}],
]


@register.inclusion_tag('components/profile/links.html')
def links():
    for link in LINKS:
        link[1]['href'] = reverse(link[0])
    return {'links': LINKS}

from urllib.parse import urljoin

from django import template

register = template.Library()

SOCIAL = {
    'facebook': 'https://www.facebook.com/',
    'twitter': 'https://twitter.com/',
    'instagram': 'https://instagram.com/',
    'youtube': 'https://youtube.com/',
    'pinterest': 'https://pinterest.com/'
}

def construct_icon(social):
    if social == 'facebook':
        social = 'facebook-f'
    base = f'fab fa-{social}'
    return base

@register.inclusion_tag('components/navs/social_link.html')
def footer_social_link(social, user_id):
    """Create a custom social tag for the footer"""
    try:
        url = SOCIAL[social]
    except:
        return {'url': '/', 'icon': '/'}
    else:
        return {'url': urljoin(url, user_id), 'icon': construct_icon(social)}

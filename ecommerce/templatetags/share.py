from django import template
from urllib.parse import urlencode

register = template.Library()

def final_url(base_url, params):
    return base_url + f'?{urlencode(params)}'

@register.simple_tag
def facebook(url):
    base_url = 'https://www.facebook.com/sharer/sharer.php'
    params = {'u': url}
    return final_url(base_url, params)

@register.simple_tag
def twitter(url, text, via):
    base_url = 'https://twitter.com/intent/tweet'
    params = {
        'text': text,
        'url': url,
        'via': via
    }
    return final_url(base_url, params)

@register.simple_tag
def pinterest(url, description, image_url):
    base_url = 'https://pinterest.com/pin/create/button/'
    params = {
        'url': url,
        'description': description,
        'media': image_url
    }
    return final_url(base_url, params)

@register.simple_tag
def email(url):
    params = {
        'utm_source': 'link',
        'utm_medium': 'email'
    }
    url = final_url(url, params)
    text = f"""
    mailto:?subject=Je suis tombé sur ce superbe article {url} et franchement ça vaut vraiment le détour.
    Je pense qu'il t'irait parfaitement!
    """
    return text

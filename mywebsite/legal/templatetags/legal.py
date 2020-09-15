from django import template
from django.template.exceptions import TemplateSyntaxError
from django.utils.safestring import mark_safe


register = template.Library()

company = {
    'name': 'Nawoka',
    'address': 'Lille',
    'domain': 'mywebsite.fr',
    'email': 'contact.mywebsite@gmail.com',
    'telephone': '',
    'services': [

    ],
    'available_days': [

    ],
    'shipping_detay': '',
    'shipping_company': 'EMA',
    'return_delay': '14 jours'
}

@register.simple_tag
def company_details(key, urlize=False):
    try:
        value = company[key]
    except KeyError:
        available_keys = company.keys()
        raise TemplateSyntaxError(('Could not get the following key "%s".'
                                   ' Available keys are %s' % (key, ', '.join(available_keys))))
    else:
        if key == 'domain':
            value = f"https://{value}/"

        if key == 'email' and urlize:
            value = mark_safe(f"<a href='mailto:{value}'>{value}</a>")

        if key == 'domain' and urlize == True:
            value = mark_safe(f"<a href='{value}'>{value}</a>")

        return value


@register.inclusion_tag('components/legal_links.html')
def legal_links():
    pass

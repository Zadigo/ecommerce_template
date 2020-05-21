from django import template

register = template.Library()

headers = {
    'users': ['id', 'name', 'username'],
    'products': ['#', 'Name', 'Country', 'Likes']
}

@register.inclusion_tag('components/others/tables/headers.html')
def header_tags(name, expand_last_by=0):
    """Create a custom social tag for the footer"""
    context = {}
    try:
        tags = headers[name]
    except:
        tags = []
    context.update({'headers': tags})
    if int(expand_last_by) > 0:
        context.update({'colspan': expand_last_by})
    return context
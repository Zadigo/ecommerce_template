from django import template

register = template.Library()

@register.inclusion_tag('components/others/tables/headers.html')
def create_table_header(*headers, expand_last_by=0):
    """Create a custom social tag for the footer"""
    context = {}
    context.update({'headers': [header for header in headers]})
    return context
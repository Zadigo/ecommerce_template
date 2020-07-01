from django import template

register = template.Library()

@register.inclusion_tag('project_components/tables/headers.html')
def header(*headers, expand_last_by=0):
    context = {}
    context.update({'headers': [header for header in headers]})
    return context

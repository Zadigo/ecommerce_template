from django.template import Library
from django import template

register = Library()

@register.simple_tag(takes_context=True)
def impressions(context, step, event, *args):
    final_list = []
    queryset = context['object_list']
    if queryset.exists():
        for item in queryset:
            impression = {}
            for arg in list(args):
                value = getattr(item, arg)
                impression.update({arg: value})
            final_list.append(impression)
    return {'impressions': final_list, 'event': event, 'step': step}

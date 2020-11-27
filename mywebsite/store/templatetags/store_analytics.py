from django.core.exceptions import ImproperlyConfigured
from django.template import Library, Node, loader
from django.utils.html import format_html

register = Library()

class SimpleAnalyticNode(Node):
    def __init__(self, queryset):
        self.queryset = queryset

    def render(self, context):
        html = ''
        templates = {
            'google_analytics': 'analytics/something.html',
            'google_tag_manager': '',
            'google_optimize': '',
            'google_ads': '',
            'facebook_pixels': '',
            'mailchimp': ''
        }
        values = self.queryset.values_list()
        keys = values.keys()
        for key in keys:
            try:
                template = templates[key]
            except:
                pass
            else:
                t = loader.get_template(template)
                html += t.render(context)
                return html


@register.simple_tag(takes_context=True)
def store_analytics(context, store):
    try:
        analytics = store.analytics_set.all()
    except:
        raise TypeError('Store is not a valid object')
    return SimpleAnalyticNode(analytics)
    

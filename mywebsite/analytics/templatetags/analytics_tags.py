from string import Template

# from analytics.models import Analytic
from django.conf import settings
from django.contrib import auth
from django.core.cache import cache
from django.db.models import query
from django.template import Library, loader
from django.template.base import Node, token_kwargs
from django.template.context import RequestContext
from django.template.exceptions import TemplateSyntaxError
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = Library()

class SimpleAnalyticNode(Node):
    def __init__(self, tags, template=None):
        self.tags = tags
        self.template = template

    def render(self, context):
        extra_context = {}
        tracking_code = self.tags.get('tag')

        if tracking_code is not None:
            extra_context = {
                'tracking_code': tracking_code.resolve(context)
            }
            template = loader.get_template(self.template)
            content = template.render(extra_context)
            return content
        else:
            return ''


class GoogleAnalyticsNode(Node):
    def __init__(self, tags):
        self.tags = tags

    def render(self, context):
        authorized_keys = [
            'analytics', 'optimize', 
                'gtm', 'remarketing'
        ]
        extra_context = {}
        for key, value in self.tags.items():
            if key not in authorized_keys:
                raise TemplateSyntaxError(
                    f"The following key '{key}' is not in the list of authorized keys. Use either: {', '.join(authorized_keys)}"
                )
            extra_context.update({key: value.resolve(context)})
        context.push(extra_context)
        return ''


@register.tag
def google_analytics_tags(parser, token):
    bits = token.split_contents()
    remaining_bits = bits[1:]
    if len(remaining_bits) < 1:
        raise TemplateSyntaxError(
            'This google analytics tag requires at least one argument'
        )
    tags = token_kwargs(
        remaining_bits, parser, support_legacy=False
    )
    return GoogleAnalyticsNode(tags)


@register.tag
def clarity(parser, token):
    bits = token.split_contents()
    remaining_bits = bits[1:]
    if len(remaining_bits) < 1:
        raise TemplateSyntaxError(
            'This tag requires at least one argument'
        )
    tags = token_kwargs(
        remaining_bits, parser, support_legacy=False
    )
    return SimpleAnalyticNode(tags, template='analytics/clarity.html')


@register.inclusion_tag('analytics/facebook.html', takes_context=True)
def facebook(context, tracking_code):
    context.push({'facebook_id': tracking_code})
    return context


@register.inclusion_tag('analytics/google_analytics.html')
def google_analytics(*args):
    tags = list(args)
    analytics_tag = None
    optimize_tag = None
    if len(tags) > 1:
        analytics_tag = tags[0]
        optimize_tag = tags[-1]
    else:
        analytics_tag = tags[-1]

    return {
        'analytics_tag': analytics_tag,
        'optimize_tag': optimize_tag,
    }


@register.inclusion_tag('analytics/optimize_anti_flicker.html')
def google_optimize_anti_flicker(tag):
    return {'optimize_tag': tag}


@register.inclusion_tag('analytics/remarketing.html')
def google_remarketing(remarketing_tag):
    return {'remarketing_tag': remarketing_tag}


@register.inclusion_tag('analytics/tag_manager.html')
def google_tag_manager(gtm_tag):
    return {'gtm_tag': gtm_tag}


@register.inclusion_tag('analytics/pinterest.html')
def pinterest(verification_code):
    return {
        'verification_code': verification_code
    }


@register.inclusion_tag('analytics/mailchimp.html')
def mailchimp(mailchimp_link):
    return {'mailchimp_link': mailchimp_link}


@register.inclusion_tag('analytics/google_no_script.html')
def google_no_script(gtm_tag):
    return {'gtm_tag': gtm_tag}

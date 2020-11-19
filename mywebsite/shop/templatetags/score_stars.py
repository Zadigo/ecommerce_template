from django.template import Library
from django.utils.html import format_html, format_html_join

register = Library()

@register.simple_tag
def stars(score):
    if isinstance(score, float):
        score = int(score)
        
    html_tags = format_html_join(
        '\n',
        '<span class="fa fa-star" value="{}"></span>',
        (str(i) for i in range(0, score))
    )
    return html_tags

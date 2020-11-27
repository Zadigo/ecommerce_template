import datetime

from django.template import Library
from django.utils.html import format_html, format_html_join

register = Library()


@register.simple_tag
def stars(score):
    if score is None:
        return ''
        
    if isinstance(score, float):
        score = int(score)

    html_tags = format_html_join(
        '\n',
        '<span class="fa fa-star" value="{}"></span>',
        (str(i) for i in range(0, score))
    )
    return html_tags


@register.simple_tag
def estimated_delivery_date(days):
    current_date = datetime.datetime.now().date()
    date_plus_fifteen = current_date + datetime.timedelta(days=days)
    upper_date = date_plus_fifteen + datetime.timedelta(days=12)
    return f"le {date_plus_fifteen.day}/{date_plus_fifteen.month} \
                    et le {upper_date.day}/{upper_date.month}"

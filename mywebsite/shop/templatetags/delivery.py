from django import template
import datetime

register = template.Library()

@register.simple_tag
def estimated_delivery_date(days):
    current_date = datetime.datetime.now().date()
    date_plus_fifteen = current_date + datetime.timedelta(days=days)
    upper_date = date_plus_fifteen + datetime.timedelta(days=12)
    return f"le {date_plus_fifteen.day}/{date_plus_fifteen.month} \
                    et le {upper_date.day}/{upper_date.month}" 

from django.template import Library
import datetime

register = Library()


@register.simple_tag
def greeting():
    current_time = datetime.datetime.now().time()
    is_night = all([
        current_time >= datetime.datetime.strptime('06:00', '%H:%M').time(),
        current_time <= datetime.datetime.strptime('00:00', '%H:%M').time(),
    ])
    if is_night:
        greeting = 'Bonsoir'
    else:
        greeting = 'Bonjour'
    return greeting

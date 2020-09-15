from cart.payment import initialize_stripe, KEYS
from django.conf import settings


def stripe_context_processor(request):
    """Return the publisheable key directly in the context
    of the application
    """
    context = dict()
    if settings.DEBUG:
        context.update({'publishable_key': KEYS['test']['publishable']})
    else:
        context.update({'publishable_key': KEYS['live']['publishable']})
    return context

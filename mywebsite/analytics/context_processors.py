from django.core.cache import cache
from analytics.models import Analytic


def get_analytics():
    analytics = cache.get('analytics')
    if not analytics:
        queryset = Analytic.objects.all()
        cache.set('analytics', analytics, 3600)
    return analytics


def analytics(request):
    return {'analytics': get_analytics()}

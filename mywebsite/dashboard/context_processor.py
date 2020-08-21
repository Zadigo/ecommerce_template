import functools

from django.core.cache import cache, caches
from django.utils.functional import cached_property

from dashboard import models


@functools.lru_cache(maxsize=2)
def dashboard(request):
    # cache = caches.all()[0]
    # old_details = cache.get('settings')
    # if old_details:
    #     return {'settings': old_details}
    # else:
    #     details = models.DashboardSetting.objects.all()
    #     cache.set('settings', details, 300)
    #     return {'settings': details}
    pass

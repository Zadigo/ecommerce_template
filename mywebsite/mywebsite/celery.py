# from __future__ import absolute_import, unicode_literals
from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mywebsite.settings')

app = Celery('mywebsite')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    pass


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

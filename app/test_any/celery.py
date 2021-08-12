from __future__ import absolute_import, unicode_literals

from django.conf import settings
import os
from celery import Celery

settings = os.getenv(
   "DJANGO_SETTINGS_MODULE", "test_any.settings_dev")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings)
app = Celery('test_any')
app.conf.broker_url = 'redis://127.0.0.1:6379'
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

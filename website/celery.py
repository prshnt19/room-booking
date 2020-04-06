from __future__ import absolute_import
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')
app = Celery('website')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.timezone = 'Asia/Kolkata'
app.conf.beat_schedule = {
    'send-report-every-single-minute': {
        'task': 'forms.task.send_feedback',
        'schedule': crontab(minute=58, hour=22),  # change to `crontab(minute=0, hour=0)` if you want it to run daily at midnight
    },
}

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

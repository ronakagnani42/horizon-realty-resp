from __future__ import absolute_import, unicode_literals
import os 
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HorizonRealityBackend.settings')
app = Celery('HorizonRealityBackend')
app.conf.enable_utc = False

app.conf.update(timezone= 'Asia/Kolkata')
app.config_from_object(settings, namespace='CELERY')

app.conf.beat_schedule = {
    'send-weekly-property-newsletter': {
        'task': 'services.tasks.send_weekly_property_newsletter',
        'schedule': crontab(hour=11, minute=0, day_of_week='1,4'),  # Every Monday and Thursday at 11 AM
    }
}

app.autodiscover_tasks()
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
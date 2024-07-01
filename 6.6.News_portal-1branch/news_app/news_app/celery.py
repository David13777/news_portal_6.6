import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_app.settings')

app = Celery('news_app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.beat_schedule = {
    'action_every_monday_8am': {
        'task': 'news_portal.weekly_mail',
        'schedule': crontab(minute='*/2')
        #'schedule': crontab(hour=8, minute=0, day_of_week='monday'),
    },
}

app.autodiscover_tasks()

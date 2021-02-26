import os

from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "toolssite.settings")

app = Celery("tool")

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "every-5-minutes": {
        "task": "tool.tasks.send_sms_notifications",
        "schedule": crontab(minute="*/5"),
        "args": (),
    },
    "every-15-minutes": {
        "task": "tool.tasks.send_email_notifications",
        "schedule": crontab(minute="*/15"),
        "args": (),
    },
    "every-hour": {
        "task": "tool.tasks.daily_notification",
        "schedule": crontab(minute=0, hour="*/1"),
        "args": (),
    },
}
app.conf.timezone = "UTC"

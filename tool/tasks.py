from django.conf import settings
import requests
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from django.utils import timezone
from schedule.models import Event


@periodic_task(run_every=(crontab(minute='*/15')), name='send_notification', ignore_result=True)
def send_notification():
    """Send email notification about events."""
    # send_mail(
    #     'Subject here',
    #     'Here is the message.',
    #     'site.hackua.com@gmail.com',
    #     ['mriynuk@gmail.com'],
    #     fail_silently=False,
    # )
    start = timezone.now() + timezone.timedelta(minutes=45)
    end = timezone.now() + timezone.timedelta(minutes=60)
    events = Event.objects.filter(start__gt=start, start__lte=end)
    for event in events:
        name = event.creator.username
        if event.creator.first_name:
            name = '{} {}'.format(event.creator.first_name, event.creator.last_name)

        text = event.description if event.description else 'No description provided'

        requests.post(
            'https://api.mailgun.net/v3/{}/messages'.format(settings.MAILGUN_SERVER_NAME),
            auth=('api', settings.MAILGUN_ACCESS_KEY),
            data={
                'from': 'Tools site <notify@{}>'.format(settings.MAILGUN_SERVER_NAME),
                'to': '{} <{}>'.format(name, event.creator.email),
                'subject': '{} will start today at {}'.format(event.title, event.start.strftime('%H:%M')),
                'text': text
            }
        )

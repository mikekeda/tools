from django.conf import settings
from django.core.mail import send_mail
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from django.utils import timezone
from schedule.models import Event
import pytz


@periodic_task(run_every=(crontab(minute='*/15')), name='send_notification', ignore_result=True)
def send_notification():
    """Send email notification about upcoming events."""
    interval = 15
    before = 60

    now = timezone.now()
    now -= timezone.timedelta(
        minutes=now.minute % interval,
        seconds=now.second,
        microseconds=now.microsecond
    )

    start = now + timezone.timedelta(minutes=before - interval)
    end = timezone.now() + timezone.timedelta(minutes=before)
    events = Event.objects.filter(start__gt=start, start__lte=end).select_related('creator')
    for event in events:
        name = event.creator.username
        if event.creator.first_name:
            name = '{} {}'.format(event.creator.first_name, event.creator.last_name)

        text = event.description if event.description else 'No description provided'
        event_time = timezone.localtime(
            event.start,
            pytz.timezone(event.creator.profile.timezone)
        ).strftime('%H:%M')

        send_mail(
            '{} will start today at {}'.format(event.title, event_time),
            text,
            'Tools site <notify@{}>'.format(settings.MAILGUN_SERVER_NAME),
            ['{} <{}>'.format(name, event.creator.email)],
        )


@periodic_task(run_every=(crontab(minute=0, hour='*/1')), name='daily_notification', ignore_result=True)
def daily_notification():
    """Send daily email notification about upcoming events."""
    sending_hour = 8

    start = timezone.now()
    end = start + timezone.timedelta(days=1)
    events = Event.objects.filter(start__gt=start, start__lte=end).select_related('creator')

    user_events = {}
    for event in events:
        local_now = timezone.localtime(
            start,
            pytz.timezone(event.creator.profile.timezone)
        )

        if local_now.hour == sending_hour:
            if event.creator.username in user_events:
                user_events[event.creator.username].append(event)
            else:
                user_events[event.creator.username] = [event]

    for username in user_events:
        text = ''
        name = username
        if user_events[username][0].creator.first_name:
            name = '{} {}'.format(
                user_events[username][0].creator.first_name,
                user_events[username][0].creator.last_name
            )

        for event in user_events[username]:
            local_time = timezone.localtime(
                event.start,
                pytz.timezone(event.creator.profile.timezone)
            ).strftime('%H:%M')

            text += '{} {}\n'.format(local_time, event.title)

        send_mail(
            "Today's events",
            text,
            'Tools site <notify@{}>'.format(settings.MAILGUN_SERVER_NAME),
            ['{} <{}>'.format(name, user_events[username][0].creator.email)],
        )

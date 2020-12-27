import pytz
from celery import Celery
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone
from schedule.models import Event
from twilio.rest import Client

app = Celery('tool')
client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


def get_occurrences(start, end, creator=None):
    """ Helper function to get events in provided period. """
    # Get events without a rule.
    query = Event.objects.filter(
        start__gt=start,
        start__lte=end,
        rule__isnull=True
    )
    if creator:
        query = query.filter(creator=creator)

    events = set(query.select_related('creator'))

    # Get events with a rule and check occurrences.
    query = Event.objects.filter(
        start__lte=end,
        rule__isnull=False
    )
    if creator:
        query = query.filter(creator=creator)
    event_list = query.filter(
        Q(end_recurring_period__gte=start) |
        Q(end_recurring_period__isnull=True)
    ).select_related('creator')
    for event in event_list:
        # get_occurrences will not include event if event end equal to end,
        # so lets add 1 microsecond to end as workaround.
        occurrences = event.get_occurrences(
            start,
            end + timezone.timedelta(microseconds=1)
        )
        if any((start < occurrence.start <= end
                for occurrence in occurrences)):
            events.add(event)

    return events


@app.task
def send_sms_notifications():
    """ Send sms notification about upcoming events. """
    interval = 5
    before = 6

    now = timezone.now()
    now -= timezone.timedelta(
        minutes=now.minute % interval,
        seconds=now.second,
        microseconds=now.microsecond
    )

    start = now + timezone.timedelta(minutes=before - interval)
    end = start + timezone.timedelta(minutes=interval)
    events = get_occurrences(start, end)

    for event in events:
        if event.creator.profile.phone_number:
            event_time = timezone.localtime(
                event.start,
                pytz.timezone(event.creator.profile.timezone)
            ).strftime('%H:%M')

            client.messages.create(
                body=f"{event.title} will start today at {event_time}",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=event.creator.profile.phone_number.as_e164
            )


@app.task
def send_email_notifications():
    """ Send email notification about upcoming events. """
    interval = 15
    before = 60

    now = timezone.now()
    now -= timezone.timedelta(
        minutes=now.minute % interval,
        seconds=now.second,
        microseconds=now.microsecond
    )

    start = now + timezone.timedelta(minutes=before - interval)
    end = start + timezone.timedelta(minutes=interval)
    events = get_occurrences(start, end)

    for event in events:
        name = event.creator.username
        if event.creator.first_name:
            name = '{} {}'.format(
                event.creator.first_name,
                event.creator.last_name
            )

        text = 'No description provided'
        if event.description:
            text = event.description

        event_time = timezone.localtime(
            event.start,
            pytz.timezone(event.creator.profile.timezone)
        ).strftime('%H:%M')

        subject = f"{event.title} will start today at {event_time}"
        html_content = render_to_string('alert-email.html', {
            'subject': subject,
            'text': text,
        })
        msg = EmailMultiAlternatives(
            subject,
            text,
            f"Tools site <notify@{settings.MAILGUN_SERVER_NAME}>",
            [f"{name} <{event.creator.email}>"],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()


@app.task
def daily_notification():
    """ Send daily email notification about upcoming events. """
    sending_hour = 8

    start = timezone.now()
    end = start + timezone.timedelta(days=1)
    events = get_occurrences(start, end)

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

        subject = "Today's events"
        html_content = render_to_string('alert-email.html', {
            'subject': subject,
            'text': text,
        })
        msg = EmailMultiAlternatives(
            subject,
            text,
            f"Tools site <notify@{settings.MAILGUN_SERVER_NAME}>",
            [f"{name} <{user_events[username][0].creator.email}>"],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

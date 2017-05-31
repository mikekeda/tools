from django.conf import settings
import requests
from celery.task.schedules import crontab
from celery.decorators import periodic_task


@periodic_task(run_every=(crontab(minute='*/5')), name='send_notification', ignore_result=True)
def send_notification():
    """Send email notification about events."""
    # send_mail(
    #     'Subject here',
    #     'Here is the message.',
    #     'site.hackua.com@gmail.com',
    #     ['mriynuk@gmail.com'],
    #     fail_silently=False,
    # )

    requests.post(
        'https://api.mailgun.net/v3/{}/messages'.format(settings.MAILGUN_DOMAIN_NAME),
        auth=("api", settings.MAILGUN_API_KEY),
        data={
            'from': 'Tools site <notify@{}>'.format(settings.MAILGUN_DOMAIN_NAME),
            'to': 'Mike <mriynuk@gmail.com>',
            'subject': 'Hello test message',
            'text': 'Testing some Mailgun!'
        }
    )

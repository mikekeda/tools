from unittest.mock import patch

import pytz
from django.utils import timezone
from schedule.models import Calendar, Event, Rule

from tool.models import Profile
from tool.tasks import daily_notification, get_occurrences, send_email_notifications
from tool.tests import BaseTestCase


class ToolTaskTest(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Profile.objects.create(user=cls.test_user, timezone="UTC")
        Profile.objects.create(user=cls.test_admin, timezone="Europe/Kiev")

        now = timezone.now()
        now -= timezone.timedelta(
            minutes=now.minute % 15, seconds=now.second, microseconds=now.microsecond
        )

        cal = Calendar.objects.create(
            name=cls.test_user.username, slug=cls.test_user.username
        )
        cls.test_event1 = Event(
            title="Test event1",
            description="Test description 1",
            start=now + timezone.timedelta(minutes=50),
            end=now + timezone.timedelta(hours=2),
            color_event="#FFA3F5",
            creator=cls.test_user,
            calendar=cal,
        )
        cls.test_event1.save()

        cal = Calendar.objects.create(
            name=cls.test_admin.username, slug=cls.test_admin.username
        )
        rule = Rule.objects.get(name="Daily")
        cls.test_event2 = Event(
            title="Test event2",
            description="Test description 2",
            start=now + timezone.timedelta(hours=2),
            end=now + timezone.timedelta(hours=4),
            color_event="#538F70",
            creator=cls.test_admin,
            calendar=cal,
            rule=rule,
        )
        cls.test_event2.save()

        cls.test_event3 = Event(
            title="Test event3",
            description="Test description 3",
            start=now + timezone.timedelta(hours=3),
            end=now + timezone.timedelta(hours=4),
            color_event="#777777",
            creator=cls.test_admin,
            calendar=cal,
        )
        cls.test_event3.save()

        cls.test_event4 = Event(
            title="Test event4",
            start=timezone.datetime(2018, 2, 23, 20, 30, tzinfo=pytz.utc),
            end=timezone.datetime(2018, 2, 23, 22, 30, tzinfo=pytz.utc),
            color_event="#999999",
            creator=cls.test_admin,
            calendar=cal,
            rule=rule,
        )
        cls.test_event4.save()

    def test_tasks_get_occurrences(self):
        start = timezone.now()
        end = start + timezone.timedelta(days=1)

        events = get_occurrences(start, end)
        self.assertSetEqual(
            events,
            {self.test_event1, self.test_event2, self.test_event3, self.test_event4},
        )

        events = get_occurrences(start, start)
        self.assertSetEqual(events, set([]))

        events = get_occurrences(start, end, self.test_user)
        self.assertSetEqual(events, {self.test_event1})

    def test_tasks_send_email_notifications(self):
        with patch("tool.tasks.EmailMultiAlternatives.send") as send_mail_mock:
            with patch("tool.tasks.timezone.localtime") as time_mock:
                time_mock.return_value.strftime.return_value = "10:30"
                send_email_notifications()
                send_mail_mock.assert_called_once()

                with patch("tool.tasks.timezone.now") as now_mock:
                    now_mock.return_value = timezone.datetime(
                        2018, 7, 23, 19, 30, tzinfo=pytz.utc
                    )
                    time_mock.return_value.strftime.return_value = "20:30"
                    send_email_notifications()
                    self.assertEqual(send_mail_mock.call_count, 2)

    def test_tasks_daily_notification(self):
        with patch("tool.tasks.EmailMultiAlternatives.send") as send_mail_mock:
            with patch("tool.tasks.timezone.localtime") as time_mock:
                time_mock.return_value.strftime.return_value = "09:15"
                # We are sending emails at 8am, too late - no calls.
                time_mock.return_value.hour = 9
                daily_notification()
                send_mail_mock.assert_not_called()

                # We are sending emails at 8am, it's time to send emails.
                time_mock.return_value.hour = 8
                daily_notification()
                self.assertEqual(send_mail_mock.call_count, 2)

import datetime
from urllib.parse import urlencode
import pytz

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from schedule.models import Calendar, Event

from .models import Profile, Card, Task, Canvas, Code, Word


class ToolViewTest(TestCase):
    def setUp(self):
        # Create usual user.
        test_user = User.objects.create_user(username='testuser',
                                             password='12345')
        test_user.save()

        # Create admin user.
        test_admin = User.objects.create_superuser(
            username='testadmin',
            email='myemail@test.com',
            password='12345'
        )
        test_admin.save()

    # Pages available for anonymous.
    def test_views_home(self):
        resp = self.client.get(reverse('main'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'text.html')

    def test_views_about(self):
        resp = self.client.get(reverse('about_page'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'about.html')

    def test_views_canvas_tool(self):
        resp = self.client.get(reverse('tool', kwargs={'slug': 'canvas'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'canvas.html')

    def test_views_canvas_tool_list(self):
        sample_1 = 'data:image/gif;base64,' +\
                   'R0lGODlhAQABAIAAAAUEBAAAACwAAAAAAQABAAACAkQBADs='
        sample_2 = 'data:image/gif;base64,' +\
                   'R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'

        resp = self.client.get(reverse('canvases',
                                       kwargs={'username': 'testuser'}))
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            {}
        )

        # Try to save something as anonymous user.
        resp = self.client.post(
            reverse('canvases', kwargs={'username': 'testuser'}),
            {'imgBase64': sample_1}
        )
        self.assertEqual(resp.status_code, 403)

        # Log in and try to save something.
        self.client.login(username='testuser', password='12345')
        resp = self.client.post(
            reverse('canvases', kwargs={'username': 'testuser'}),
            {'imgBase64': sample_1}
        )
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(reverse('canvases',
                                       kwargs={'username': 'testuser'}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)
        self.assertEqual(list(resp.json().values())[0], sample_1)

        # Try to change something.
        slug = list(resp.json().keys())[0]
        resp = self.client.post(
            reverse('canvases', kwargs={'username': 'testuser'}),
            {'imgBase64': sample_2, 'slug': slug}
        )
        self.assertEqual(resp.status_code, 200)

        # Try to change not existing canvas.
        resp = self.client.post(
            reverse('canvases', kwargs={'username': 'testuser'}),
            {'imgBase64': sample_2, 'slug': 'not-exists'}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)
        self.assertEqual(list(resp.json().values())[0], sample_2)

        resp = self.client.get(reverse('canvases',
                                       kwargs={'username': 'testuser'}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)
        self.assertEqual(list(resp.json().values())[0], sample_2)

        # Regular user can't create canvas for another user.
        resp = self.client.post(
            reverse('canvases', kwargs={'username': 'testadmin'}),
            {'imgBase64': sample_2}
        )
        self.assertEqual(resp.status_code, 403)

        # Admin can change canvas for another user.
        self.client.login(username='testadmin', password='12345')
        resp = self.client.post(
            reverse('canvases', kwargs={'username': 'testuser'}),
            {'imgBase64': sample_1}
        )
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(reverse('canvases',
                                       kwargs={'username': 'testuser'}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 2)
        self.assertEqual(sorted(list(resp.json().values()))[0], sample_2)
        self.assertEqual(sorted(list(resp.json().values()))[1], sample_1)

    def test_views_canvas(self):
        sample_1 = 'data:image/gif;base64,' +\
                   'R0lGODlhAQABAIAAAAUEBAAAACwAAAAAAQABAAACAkQBADs='

        # Log in and try to save something.
        self.client.login(username='testuser', password='12345')
        resp = self.client.post(
            reverse('canvases', kwargs={'username': 'testuser'}),
            {'imgBase64': sample_1}
        )
        self.assertEqual(resp.status_code, 200)

        user = User.objects.get(username='testuser')
        test_canvas = Canvas.objects.get(user=user)
        self.assertEqual(str(test_canvas), 'testuser: 1')

        resp = self.client.get(reverse('canvas',
                                       kwargs={'slug': test_canvas.slug}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), sample_1)

    def test_views_convert_image_tool(self):
        resp = self.client.get(reverse(
            'tool',
            kwargs={'slug': 'convert-image-to-base64'}
        ))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'convert-image-to-base64.html')

    def test_views_image_info_tool(self):
        resp = self.client.get(reverse('tool',
                                       kwargs={'slug': 'get-image-exif-info'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'get-image-exif-info.html')

    def test_views_text_tool(self):
        resp = self.client.get(reverse('tool', kwargs={'slug': 'text'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'text.html')

    def test_views_units_converter_tool(self):
        resp = self.client.get(reverse('tool',
                                       kwargs={'slug': 'units-converter'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'units-converter.html')

    def test_views_notexisting_tool(self):
        resp = self.client.get(reverse('tool',
                                       kwargs={'slug': 'notexisting'}))
        self.assertEqual(resp.status_code, 404)
        self.assertTemplateUsed(resp, '404.html')

    # Pages available only for registered users.
    def test_views_tool_notexisting_user(self):
        resp = self.client.get(reverse('user_tool', kwargs={
            'username': 'notexisting',
            'slug': 'text'
        }))
        self.assertEqual(resp.status_code, 404)
        self.assertTemplateUsed(resp, '404.html')

    def test_views_events(self):
        resp = self.client.get(reverse('events'))
        self.assertRedirects(resp, '/login?next=/events')

        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('events'))
        self.assertEqual(resp.status_code, 404)
        self.assertTemplateUsed(resp, '404.html')

        resp = self.client.get(
            reverse('events'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            str(resp.content, encoding='utf8'),
            '""'
        )

        # Create an event.
        test_user = User.objects.get(username='testuser')
        cal = Calendar.objects.create(name="testuser")
        start = timezone.now() + timezone.timedelta(hours=2)
        test_event1 = Event(
            title='Test event',
            description='Test description 3',
            start=start,
            end=start + timezone.timedelta(hours=2),
            color_event='#FFA3F5',
            creator=test_user,
            calendar=cal
        )
        test_event1.save()

        resp = self.client.get(
            reverse('events'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            str(resp.content, encoding='utf8'),
            '"{} Test event"'.format(start.strftime('%H:%M'))
        )

        # Set user timezone (event should be aware of user's timezone).
        profile = Profile.objects.get(user=test_user)
        profile.timezone = 'Europe/Kiev'
        profile.save()
        local_start = timezone.localtime(start, pytz.timezone('Europe/Kiev'))
        resp = self.client.get(
            reverse('events'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            str(resp.content, encoding='utf8'),
            '"{} Test event"'.format(local_start.strftime('%H:%M'))
        )

    def test_views_calendar_get(self):
        resp = self.client.get(reverse('calendar'))
        self.assertRedirects(resp, '/login?next=/calendar')
        resp = self.client.get(reverse('user_calendar',
                                       kwargs={'username': 'testuser'}))
        self.assertRedirects(resp,
                             '/login?next=/user/testuser/calendar')
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('calendar'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'calendar.html')
        resp = self.client.get(reverse('user_calendar',
                                       kwargs={'username': 'testuser'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'calendar.html')

        # Admin can see user's events.
        self.client.login(username='testadmin', password='12345')
        resp = self.client.get(reverse('user_calendar',
                                       kwargs={'username': 'testuser'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'calendar.html')

    def test_views_calendar_post(self):
        # Create an event.
        resp = self.client.post(reverse('calendar'), {
            'title': 'Test title',
            'description': 'Test description',
            'start': '2018-01-17 19:27',
            'end': '2018-01-27 19:28',
            'color_event': 'EBDFD6',
            'rule': 4,
        })
        self.assertRedirects(resp, '/login?next=/calendar')
        self.client.login(username='testuser', password='12345')
        # Title can't be empty.
        resp = self.client.post(reverse('calendar'), {
            'title': '',
            'description': 'Test description',
            'start': '2018-01-17 19:27',
            'end': '2018-01-27 19:28',
            'color_event': 'EBDFD6',
            'rule': 4,
        })
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post(reverse('calendar'), {
            'title': 'Test title',
            'description': 'Test description',
            'start': '2018-01-17 19:27',
            'end': '2018-01-27 19:28',
            'color_event': 'EBDFD6',
            'rule': 4,
        })
        self.assertRedirects(resp, reverse('calendar'))
        test_user = User.objects.get(username='testuser')
        test_event = Event.objects.get(title='Test title', creator=test_user)
        self.assertEqual(test_event.description, 'Test description')
        self.assertEqual(test_event.color_event, '#EBDFD6')

        # Admin can create an event for any user.
        self.client.login(username='testadmin', password='12345')
        resp = self.client.post(
            reverse('user_calendar', kwargs={'username': 'testuser'}),
            {
                'title': 'Test title admin',
                'description': 'Test description admin',
                'start': '2018-01-20 19:27',
                'end': '2018-01-21 19:28',
                'color_event': '7DA2FF',
                'rule': 2,
            }
        )
        self.assertRedirects(resp, reverse('user_calendar',
                                           kwargs={'username': 'testuser'}))
        test_event_admin = Event.objects.get(title='Test title admin',
                                             creator=test_user)
        self.assertEqual(test_event_admin.description,
                         'Test description admin')
        self.assertEqual(test_event_admin.color_event, '#7DA2FF')
        self.client.logout()

        # Edit the event.
        resp = self.client.post(reverse('calendar'), {
            'id': test_event_admin.pk,
            'title': 'Test title user',
            'description': 'Test description user',
            'start': '2018-02-20 19:27',
            'end': '2018-02-21 19:28',
            'color_event': 'FFA3F5',
            'rule': 3,
        })
        self.assertRedirects(resp, '/login?next=/calendar')
        self.client.login(username='testuser', password='12345')
        resp = self.client.post(reverse('calendar'), {
            'id': test_event_admin.pk,
            'title': 'Test title user',
            'description': 'Test description user',
            'start': '2018-02-20 19:27',
            'end': '2018-02-21 19:28',
            'color_event': 'FFA3F5',
            'rule': 3,
        })
        self.assertRedirects(resp, reverse('calendar'))
        test_event_admin = Event.objects.get(pk=test_event_admin.pk)
        self.assertEqual(test_event_admin.title, 'Test title user')
        self.assertEqual(test_event_admin.description, 'Test description user')
        self.assertEqual(test_event_admin.color_event, '#FFA3F5')
        # Try to edit not existing event.
        resp = self.client.post(reverse('calendar'), {
            'id': 77777,
            'title': 'Test title not exists',
            'description': 'Test description not exists',
            'start': '2018-04-20 19:27',
            'end': '2018-04-21 19:28',
            'color_event': '4549FF',
            'rule': 1,
        })
        self.assertEqual(resp.status_code, 404)

        # Admin can edit an event for any user.
        self.client.login(username='testadmin', password='12345')
        resp = self.client.post(
            reverse('user_calendar', kwargs={'username': 'testuser'}),
            {
                'id': test_event.pk,
                'title': 'Test title admin 2',
                'description': 'Test description admin 2',
                'start': '2018-06-20 19:27',
                'end': '2018-06-21 19:28',
                'color_event': 'FFC678',
                'rule': 2,
            }
        )
        self.assertRedirects(resp, reverse('user_calendar',
                                           kwargs={'username': 'testuser'}))
        test_event = Event.objects.get(pk=test_event.pk)
        self.assertEqual(test_event.title, 'Test title admin 2')
        self.assertEqual(test_event.description, 'Test description admin 2')
        self.assertEqual(test_event.color_event, '#FFC678')

        # Set user timezone (event should be aware of user's timezone).
        profile = Profile.objects.get(user=test_user)
        profile.timezone = 'Europe/Kiev'
        profile.save()
        # Edit user event.
        resp = self.client.post(
            reverse('user_calendar', kwargs={'username': 'testuser'}),
            {
                'id': test_event.pk,
                'title': 'Test title admin 3',
                'description': 'Test description admin 3',
                'start': '2022-02-20 11:27',
                'end': '2022-02-21 11:28',
                'color_event': 'FFC677',
                'rule': 2,
            }
        )
        self.assertRedirects(resp, reverse('user_calendar',
                                           kwargs={'username': 'testuser'}))
        test_event = Event.objects.get(pk=test_event.pk)
        self.assertEqual(test_event.title, 'Test title admin 3')
        self.assertEqual(test_event.description, 'Test description admin 3')
        self.assertEqual(test_event.color_event, '#FFC677')
        self.assertEqual(
            test_event.start,
            datetime.datetime(2022, 2, 20, 9, 27, tzinfo=pytz.utc)
        )
        self.assertEqual(
            test_event.end,
            datetime.datetime(2022, 2, 21, 9, 28, tzinfo=pytz.utc)
        )

    def test_views_calendar_delete(self):
        test_user = User.objects.get(username='testuser')
        cal = Calendar.objects.create(name="testuser")
        test_event1 = Event(
            title='Test title 3',
            description='Test description 3',
            start=datetime.datetime(2018, 1, 5, 8, 0, tzinfo=pytz.utc),
            end=datetime.datetime(2018, 1, 5, 9, 0, tzinfo=pytz.utc),
            color_event='#FFA3F5',
            creator=test_user,
            calendar=cal
        )
        test_event1.save()

        test_event2 = Event(
            title='Test title 3 admin',
            description='Test description 3 admin',
            start=datetime.datetime(2018, 1, 4, 8, 0, tzinfo=pytz.utc),
            end=datetime.datetime(2018, 1, 4, 10, 0, tzinfo=pytz.utc),
            color_event='#A3E2FF',
            creator=test_user,
            calendar=cal
        )
        test_event2.save()
        # Delete event.
        resp = self.client.delete(
            reverse('calendar_pk', kwargs={'pk': test_event1.pk})
        )
        self.assertRedirects(
            resp,
            '/login?next=/calendar/' + str(test_event1.pk)
        )
        self.client.login(username='testuser', password='12345')
        resp = self.client.delete(reverse('calendar_pk', kwargs={'pk': 77777}))
        self.assertEqual(resp.status_code, 404)
        resp = self.client.delete(
            reverse('calendar_pk', kwargs={'pk': test_event1.pk})
        )
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            {'redirect': '/calendar', 'success': True}
        )
        test_event1_exists = Event.objects.filter(
            pk=test_event1.pk
        ).exists()
        self.assertFalse(test_event1_exists)

        # Admin can delete an event for any user.
        self.client.login(username='testadmin', password='12345')
        resp = self.client.delete(
            reverse('user_calendar_pk', kwargs={'pk': test_event2.pk,
                                                'username': 'testuser'})
        )
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            {'redirect': '/user/testuser/calendar', 'success': True}
        )
        test_event2_exists = Event.objects.filter(
            pk=test_event2.pk
        ).exists()
        self.assertFalse(test_event2_exists)

    def test_views_flights(self):
        resp = self.client.get(reverse('flights'))
        self.assertRedirects(resp, '/login?next=/flights')

        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('flights'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'flights.html')

        resp = self.client.post(reverse('flights'), {
            'destination': 'LWO',
            'round_trip': 'on',
            'date_start': '2017-12-16',
            'date_back': '2017-12-23',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'origin',
                             'This field is required.')

        resp = self.client.post(reverse('flights'), {
            'origin': 'AUS',
            'destination': 'LWO',
            'round_trip': 'on',
            'date_start': '2017-12-16',
            'date_back': '2017-12-23',
        })
        self.assertEqual(resp.status_code, 200)

    def test_views_dictionary_get(self):
        resp = self.client.get(reverse('dictionary'))
        self.assertRedirects(resp, '/login?next=/dictionary')
        resp = self.client.get(reverse('user_dictionary',
                                       kwargs={'username': 'testuser'}))
        self.assertRedirects(resp,
                             '/login?next=/user/testuser/dictionary')
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('dictionary'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'dictionary.html')
        resp = self.client.get(reverse('user_dictionary',
                                       kwargs={'username': 'testuser'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'dictionary.html')

    def test_views_dictionary_post(self):
        # Anonymous user - redirect.
        resp = self.client.post(reverse('dictionary'), {
            lang[0]: 'test' + lang[0]
            for lang in settings.LANGUAGES
        })
        self.assertEqual(resp.status_code, 403)

        # Registered user.
        self.client.login(username='testuser', password='12345')
        resp = self.client.post(reverse('dictionary'), {
            lang[0]: 'test' + lang[0]
            for lang in settings.LANGUAGES
        })
        self.assertRedirects(resp, '/dictionary')
        test_user = User.objects.get(username='testuser')
        test_word = Word.objects.get(en='testen', user=test_user)
        self.assertEqual(test_word.es, 'testes')

        # Admin user - can create a new word for any user.
        self.client.login(username='testadmin', password='12345')
        resp = self.client.post(
            reverse('user_dictionary', kwargs={'username': 'testuser'}),
            {lang[0]: 'testadmin' + lang[0] for lang in settings.LANGUAGES}
        )
        self.assertRedirects(resp, '/user/testuser/dictionary')
        test_word = Word.objects.get(en='testadminen', user=test_user)
        self.assertEqual(test_word.es, 'testadmines')

    def test_views_dictionary_put(self):
        test_user = User.objects.get(username='testuser')
        test_word = Word(en='testen', es='testes', user=test_user)
        test_word.save()
        self.assertEqual(str(test_word), 'testen')

        # Anonymous user - redirect.
        resp = self.client.put(
            path=reverse('dictionary'),
            data=urlencode({
                'pk': test_word.pk,
                'lang': 'en',
                'value': 'put_test_anonymous_en',
            }),
            content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(resp.status_code, 403)

        # Registered user.
        self.client.login(username='testuser', password='12345')
        resp = self.client.put(
            path=reverse('dictionary'),
            data=urlencode({
                'pk': test_word.pk,
                'lang': 'en',
                'value': 'put_test_en',
            }),
            content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            {'redirect': '/dictionary', 'success': True}
        )
        test_word = Word.objects.get(pk=test_word.pk)
        self.assertEqual(test_word.en, 'put_test_en')
        # Not valid lang.
        resp = self.client.put(
            path=reverse('dictionary'),
            data=urlencode({
                'pk': test_word.pk,
                'lang': 'dummy',
                'value': 'put_test_dummy',
            }),
            content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(
            str(resp.content, encoding='utf8'),
            '"You can\'t change this field"'
        )

        # Admin user - can edit any word for any user.
        self.client.login(username='testadmin', password='12345')
        resp = self.client.put(
            path=reverse('dictionary'),
            data=urlencode({
                'pk': test_word.pk,
                'lang': 'en',
                'value': 'put_test_admin_en',
            }),
            content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            {'redirect': '/dictionary', 'success': True}
        )
        test_word = Word.objects.get(pk=test_word.pk)
        self.assertEqual(test_word.en, 'put_test_admin_en')

    def test_views_flashcards_get(self):
        resp = self.client.get(reverse('flashcards'))
        self.assertRedirects(resp, '/login?next=/flashcards')
        resp = self.client.get(reverse('user_flashcards',
                                       kwargs={'username': 'testuser'}))
        self.assertRedirects(resp,
                             '/login?next=/user/testuser/flashcards')
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('flashcards'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'flashcards.html')
        resp = self.client.get(reverse('user_flashcards',
                                       kwargs={'username': 'testuser'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'flashcards.html')

        # Admin can see user's flashcards.
        self.client.login(username='testadmin', password='12345')
        resp = self.client.get(reverse('user_flashcards',
                                       kwargs={'username': 'testuser'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'flashcards.html')

    def test_views_flashcards_post(self):
        # Create a flashcard.
        resp = self.client.post(reverse('flashcards'), {
            'word': 'Test flashcard',
            'description': 'Dummy text',
            'difficulty': 'middle',
        })
        self.assertRedirects(resp, '/login?next=/flashcards')
        self.client.login(username='testuser', password='12345')
        # Title can't be empty.
        resp = self.client.post(reverse('flashcards'), {
            'word': '',
            'description': 'Dummy text',
            'difficulty': 'middle',
        })
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post(reverse('flashcards'), {
            'word': 'Test flashcard',
            'description': 'Dummy text',
            'difficulty': 'middle',
        })
        self.assertRedirects(resp, reverse('flashcards'))
        test_user = User.objects.get(username='testuser')
        test_flashcard = Card.objects.get(word='Test flashcard',
                                          user=test_user)
        self.assertEqual(test_flashcard.description, 'Dummy text')
        # Word should be unique.
        resp = self.client.post(reverse('flashcards'), {
            'word': 'Test flashcard',
            'description': 'Dummy text 2',
            'difficulty': 'easy',
        })
        self.assertEqual(resp.status_code, 200)
        test_flashcard = Card.objects.get(word='Test flashcard',
                                          user=test_user)
        self.assertEqual(test_flashcard.description, 'Dummy text')

        # Admin can create a flashcard for any user.
        self.client.login(username='testadmin', password='12345')
        resp = self.client.post(
            reverse('user_flashcards', kwargs={'username': 'testuser'}),
            {
                'word': 'Test flashcard admin',
                'description': 'Dummy text admin',
                'difficulty': 'easy',
            }
        )
        self.assertRedirects(resp, reverse('user_flashcards',
                                           kwargs={'username': 'testuser'}))
        test_flashcard_admin = Card.objects.get(word='Test flashcard admin',
                                                user=test_user)
        self.assertEqual(test_flashcard_admin.description, 'Dummy text admin')
        self.client.logout()

        # Edit the flashcard.
        resp = self.client.post(reverse('flashcards'), {
            'id': test_flashcard_admin.pk,
            'word': 'Test flashcard user',
            'description': 'Dummy text user',
            'difficulty': 'difficult',
        })
        self.assertRedirects(resp, '/login?next=/flashcards')
        self.client.login(username='testuser', password='12345')
        resp = self.client.post(reverse('flashcards'), {
            'id': test_flashcard_admin.pk,
            'word': 'Test flashcard user',
            'description': 'Dummy text user',
            'difficulty': 'difficult',
        })
        self.assertRedirects(resp, reverse('flashcards'))
        test_flashcard_admin = Card.objects.get(pk=test_flashcard_admin.pk)
        self.assertEqual(test_flashcard_admin.word, 'Test flashcard user')
        self.assertEqual(test_flashcard_admin.description, 'Dummy text user')
        self.assertEqual(test_flashcard_admin.difficulty, 'difficult')
        # Try to edit not existing flashcard.
        resp = self.client.post(reverse('flashcards'), {
            'id': 77777,
            'word': 'Test flashcard user',
            'description': 'Dummy text user',
            'difficulty': 'difficult',
        })
        self.assertEqual(resp.status_code, 404)

        # Admin can edit a flashcard for any user.
        self.client.login(username='testadmin', password='12345')
        resp = self.client.post(
            reverse('user_flashcards', kwargs={'username': 'testuser'}),
            {
                'id': test_flashcard.pk,
                'word': 'Test flashcard admin 2',
                'description': 'Dummy text admin 2',
                'difficulty': 'middle',
            }
        )
        self.assertRedirects(resp, reverse('user_flashcards',
                                           kwargs={'username': 'testuser'}))
        test_flashcard = Card.objects.get(pk=test_flashcard.pk)
        self.assertEqual(test_flashcard.word, 'Test flashcard admin 2')
        self.assertEqual(test_flashcard.description, 'Dummy text admin 2')
        self.assertEqual(test_flashcard.difficulty, 'middle')

    def test_views_flashcards_delete(self):
        test_user = User.objects.get(username='testuser')
        test_flashcard = Card(
            word='Test flashcard 3',
            user=test_user,
            description='Dummy text 3',
            difficulty='middle',
        )
        test_flashcard.save()
        self.assertEqual(str(test_flashcard), 'Test flashcard 3')
        test_flashcard_admin = Card(
            word='Test flashcard admin',
            user=test_user,
            description='Dummy text admin',
            difficulty='middle',
        )
        test_flashcard_admin.save()
        self.assertEqual(str(test_flashcard_admin), 'Test flashcard admin')
        # Delete flashcard.
        resp = self.client.delete(
            reverse('flashcards_pk', kwargs={'pk': test_flashcard.pk})
        )
        self.assertRedirects(
            resp,
            '/login?next=/flashcards/' + str(test_flashcard.pk)
        )
        self.client.login(username='testuser', password='12345')
        resp = self.client.delete(
            reverse('flashcards_pk', kwargs={'pk': 77777})
        )
        self.assertEqual(resp.status_code, 404)
        resp = self.client.delete(
            reverse('flashcards_pk', kwargs={'pk': test_flashcard.pk})
        )
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            {'redirect': '/flashcards', 'success': True}
        )
        test_flashcard_exists = Card.objects.filter(
            pk=test_flashcard.pk
        ).exists()
        self.assertFalse(test_flashcard_exists)

        # Admin can delete a flashcard for any user.
        self.client.login(username='testadmin', password='12345')
        resp = self.client.delete(
            reverse('flashcards_pk', kwargs={'pk': test_flashcard_admin.pk})
        )
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            {'redirect': '/flashcards', 'success': True}
        )
        test_flashcard_admin_exists = Card.objects.filter(
            pk=test_flashcard_admin.pk
        ).exists()
        self.assertFalse(test_flashcard_admin_exists)

    def test_views_flashcards_order(self):
        resp = self.client.post(reverse('card_order',
                                        kwargs={'username': 'testuser'}),
                                {'order': '{}'})
        self.assertRedirects(resp, '/login?next=/user/testuser/card-order')

        self.client.login(username='testuser', password='12345')
        resp = self.client.post(reverse('card_order',
                                        kwargs={'username': 'testuser'}),
                                {'order': '{}'})
        self.assertEqual(resp.status_code, 404)
        self.assertTemplateUsed(resp, '404.html')

        resp = self.client.post(
            reverse('card_order', kwargs={'username': 'testuser'}),
            {'order': '{}'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            str(resp.content, encoding='utf8'),
            '"The order was changed"'
        )

    def test_views_tasks_get(self):
        resp = self.client.get(reverse('tasks'))
        self.assertRedirects(resp, '/login?next=/tasks')
        resp = self.client.get(reverse('user_tasks',
                                       kwargs={'username': 'testuser'}))
        self.assertRedirects(resp, '/login?next=/user/testuser/tasks')
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('tasks'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'tasks.html')
        resp = self.client.get(reverse('user_tasks',
                                       kwargs={'username': 'testuser'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'tasks.html')

        # Admin can see user's tasks.
        self.client.login(username='testadmin', password='12345')
        resp = self.client.get(reverse('user_tasks',
                                       kwargs={'username': 'testuser'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'tasks.html')

    def test_views_tasks_post(self):
        # Create a task.
        resp = self.client.post(reverse('tasks'), {
            'title': 'Test task',
            'description': 'Dummy text',
            'color': 1,
        })
        self.assertRedirects(resp, '/login?next=/tasks')
        self.client.login(username='testuser', password='12345')
        resp = self.client.post(reverse('tasks'), {
            'title': 'Test task',
            'description': 'Dummy text',
            'color': 1,
        })
        self.assertRedirects(resp, reverse('tasks'))
        test_user = User.objects.get(username='testuser')
        test_task = Task.objects.get(title='Test task', user=test_user)
        self.assertEqual(test_task.description, 'Dummy text')

        # Admin can create a task for any user.
        self.client.login(username='testadmin', password='12345')
        resp = self.client.post(
            reverse('user_tasks', kwargs={'username': 'testuser'}),
            {
                'title': 'Test task admin',
                'description': 'Dummy text admin',
                'color': 5,
            }
        )
        self.assertRedirects(resp, reverse('user_tasks',
                                           kwargs={'username': 'testuser'}))
        test_task_admin = Task.objects.get(title='Test task admin',
                                           user=test_user)
        self.assertEqual(test_task_admin.description, 'Dummy text admin')
        self.assertEqual(test_task_admin.color, 5)
        self.client.logout()

        # Edit the task.
        resp = self.client.post(reverse('tasks'), {
            'id': test_task.pk,
            'title': 'Test task 3',
            'description': 'Dummy text 3',
            'color': 3,
        })
        self.assertRedirects(resp, '/login?next=/tasks')
        self.client.login(username='testuser', password='12345')
        resp = self.client.post(reverse('tasks'), {
            'id': test_task.pk,
            'title': 'Test task 3',
            'description': 'Dummy text 3',
            'color': 3,
        })
        self.assertRedirects(resp, reverse('tasks'))
        test_task = Task.objects.get(title='Test task 3', user=test_user)
        self.assertEqual(test_task.description, 'Dummy text 3')
        self.assertEqual(test_task.color, 3)
        # Try to edit not existing task.
        resp = self.client.post(reverse('tasks'), {
            'id': 77777,
            'title': 'Test task 3',
            'description': 'Dummy text 3',
            'color': 3,
        })
        self.assertEqual(resp.status_code, 404)

        # Admin can edit a task for any user.
        self.client.login(username='testadmin', password='12345')
        resp = self.client.post(
            reverse('user_tasks', kwargs={'username': 'testuser'}),
            {
                'id': test_task.pk,
                'title': 'Test title admin 2',
                'description': 'Dummy text admin 2',
                'color': 2,
            }
        )
        self.assertRedirects(resp, reverse('user_tasks',
                                           kwargs={'username': 'testuser'}))
        test_flashcard = Task.objects.get(pk=test_task.pk)
        self.assertEqual(test_flashcard.title, 'Test title admin 2')
        self.assertEqual(test_flashcard.description, 'Dummy text admin 2')
        self.assertEqual(test_flashcard.color, 2)

        # Try to post not valid form.
        resp = self.client.post(
            reverse('user_tasks', kwargs={'username': 'testuser'}),
            {}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'tasks.html')
        test_flashcard = Task.objects.get(pk=test_task.pk)
        self.assertEqual(test_flashcard.title, 'Test title admin 2')
        self.assertEqual(test_flashcard.description, 'Dummy text admin 2')
        self.assertEqual(test_flashcard.color, 2)

    def test_views_tasks_delete(self):
        test_user = User.objects.get(username='testuser')
        test_task = Task(
            title='Test task 3',
            user=test_user,
            description='Dummy text 3',
            color=3,
        )
        test_task.save()
        self.assertEqual(str(test_task), 'Test task 3')
        test_task_admin = Task(
            title='Test task admin',
            user=test_user,
            description='Dummy text admin',
            color=5,
        )
        test_task_admin.save()
        self.assertEqual(str(test_task_admin), 'Test task admin')
        # Delete the task.
        resp = self.client.delete(
            reverse('tasks_pk', kwargs={'pk': test_task.pk})
        )
        self.assertRedirects(
            resp,
            '/login?next=/tasks/' + str(test_task.pk)
        )
        self.client.login(username='testuser', password='12345')
        resp = self.client.delete(
            reverse('tasks_pk', kwargs={'pk': 77777})
        )
        self.assertEqual(resp.status_code, 404)
        resp = self.client.delete(
            reverse('tasks_pk', kwargs={'pk': test_task.pk})
        )
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            {'redirect': '/tasks', 'success': True}
        )
        test_task_exists = Task.objects.filter(pk=test_task.pk).exists()
        self.assertFalse(test_task_exists)

        # Admin can delete a task for any user.
        self.client.login(username='testadmin', password='12345')
        resp = self.client.delete(
            reverse('tasks_pk', kwargs={'pk': test_task_admin.pk})
        )
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            {'redirect': '/tasks', 'success': True}
        )
        test_task_admin_exists = Task.objects.filter(
            pk=test_task_admin.pk
        ).exists()
        self.assertFalse(test_task_admin_exists)

    def test_views_tasks_order(self):
        resp = self.client.post(reverse('task_order',
                                        kwargs={'username': 'testuser'}),
                                {'order': '{}', 'status': '{}'})
        self.assertRedirects(resp, '/login?next=/user/testuser/task-order')

        self.client.login(username='testuser', password='12345')
        resp = self.client.post(reverse('task_order',
                                        kwargs={'username': 'testuser'}),
                                {'order': '{}', 'status': '{}'})
        self.assertEqual(resp.status_code, 404)
        self.assertTemplateUsed(resp, '404.html')

        resp = self.client.post(
            reverse('task_order', kwargs={'username': 'testuser'}),
            {'order': '{}', 'status': '{}'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            str(resp.content, encoding='utf8'),
            '{"task": {}}'
        )

    def test_views_code_snippets_get(self):
        # Get user's code snippets.
        resp = self.client.get(reverse('code'))
        self.assertRedirects(resp, '/login?next=/code')

        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('code'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'code.html')
        # Filter by label.
        resp = self.client.get(reverse('code') + '?label=test')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'code.html')

    def test_views_code_snippets_post(self):
        # Create code snippet.
        self.client.login(username='testuser', password='12345')
        resp = self.client.post(reverse('code'), {
            'title': 'Test code snippet',
            'text': '<pre><code>print(1)<code><pre>',
        })
        self.assertRedirects(resp, '/code')
        test_user = User.objects.get(username='testuser')
        test_code_snippet = Code.objects.get(title='Test code snippet',
                                             user=test_user)
        self.assertEqual(test_code_snippet.text,
                         '<pre><code>print(1)<code><pre>')
        # Title should be unique.
        resp = self.client.post(reverse('code'), {
            'title': 'Test code snippet',
            'text': '<pre><code>print(2)<code><pre>',
        })
        self.assertEqual(resp.status_code, 200)
        test_code_snippet = Code.objects.get(title='Test code snippet',
                                             user=test_user)
        self.assertEqual(test_code_snippet.text,
                         '<pre><code>print(1)<code><pre>')
        # Text should not be empty.
        resp = self.client.post(reverse('code'), {
            'title': 'Test code snippet',
            'text': '',
        })
        self.assertEqual(resp.status_code, 200)
        test_code_snippet = Code.objects.get(title='Test code snippet',
                                             user=test_user)
        self.assertEqual(test_code_snippet.text,
                         '<pre><code>print(1)<code><pre>')
        self.client.logout()

        # Get user code snippet.
        resp = self.client.get(
            reverse('code_slug', kwargs={'slug': test_code_snippet.slug})
        )
        self.assertTemplateUsed(resp, 'code.html')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get(
            reverse('code_slug', kwargs={'slug': 'not-exists'})
        )
        self.assertEqual(resp.status_code, 404)

        # Change code snippet.
        resp = self.client.post(
            reverse('code_slug', kwargs={'slug': test_code_snippet.slug}),
            {
                'title': 'Test code snippet 2',
                'text': '<pre><code>print(2)<code><pre>',
            }
        )
        self.assertEqual(resp.status_code, 403)
        self.client.login(username='testuser', password='12345')
        resp = self.client.post(
            reverse('code_slug', kwargs={'slug': test_code_snippet.slug}),
            {
                'title': 'Test code snippet 2',
                'text': '<pre><code>print(2)<code><pre>',
            }
        )
        self.assertRedirects(resp, '/code')
        test_code_snippet = Code.objects.get(title='Test code snippet 2',
                                             user=test_user)
        self.assertTrue(test_code_snippet)
        self.assertEqual(test_code_snippet.text,
                         '<pre><code>print(2)<code><pre>')
        # Text should not be empty.
        resp = self.client.post(
            reverse('code_slug', kwargs={'slug': test_code_snippet.slug}),
            {
                'title': 'Test code snippet 2',
                'text': '',
            }
        )
        self.assertEqual(resp.status_code, 200)
        test_code_snippet = Code.objects.get(title='Test code snippet 2',
                                             user=test_user)
        self.assertEqual(test_code_snippet.text,
                         '<pre><code>print(2)<code><pre>')
        self.client.logout()

    def test_views_code_snippets_delete(self):
        test_user = User.objects.get(username='testuser')
        test_code_snippet = Code(title='test1', text='code block 1',
                                 user=test_user)
        test_code_snippet.save()

        # Delete code snippet.
        resp = self.client.delete(
            reverse('code_slug', kwargs={'slug': test_code_snippet.slug})
        )
        self.assertEqual(resp.status_code, 403)
        self.client.login(username='testuser', password='12345')
        resp = self.client.delete(
            reverse('code_slug', kwargs={'slug': 'not-exists'})
        )
        self.assertEqual(resp.status_code, 404)
        resp = self.client.delete(
            reverse('code_slug', kwargs={'slug': test_code_snippet.slug})
        )
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            {'redirect': '/code', 'success': True}
        )
        test_code_snippet_exists = Code.objects.filter(
            slug=test_code_snippet.slug
        ).exists()
        self.assertFalse(test_code_snippet_exists)

    def test_views_profile(self):
        resp = self.client.get(reverse('user',
                                       kwargs={'username': 'testuser'}))
        self.assertRedirects(resp, '/login?next=/user/testuser')
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('user',
                                       kwargs={'username': 'testuser'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'profile.html')

    # Special pages.
    def test_views_sitemap(self):
        resp = self.client.get('/sitemap.xml')
        self.assertEqual(resp.status_code, 200)

    def test_views_login(self):
        resp = self.client.get(reverse('login'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'login.html')

        # Try to login again (fail).
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('login'))
        self.assertRedirects(resp, settings.LOGIN_REDIRECT_URL)

    def test_views_logout(self):
        resp = self.client.get(reverse('logout'))
        self.assertRedirects(resp, '/login?next=/logout')

        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('logout'))
        self.assertRedirects(resp, reverse('login'))

    def test_views_users(self):
        resp = self.client.get(reverse('users'))
        self.assertRedirects(resp, '/admin/login/?next=/users')
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('users'))
        self.assertRedirects(resp, '/admin/login/?next=/users')
        self.client.login(username='testadmin', password='12345')
        resp = self.client.get(reverse('users'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'user_list.html')

    def test_views_update_profile(self):
        resp = self.client.post(
            reverse('user', kwargs={'username': 'testuser'}),
            {'first_name': 'test1'}
        )
        self.assertRedirects(resp, '/login?next=/user/testuser')
        self.client.login(username='testuser', password='12345')
        # Need to create profile for the users.
        resp = self.client.get(reverse('user',
                                       kwargs={'username': 'testuser'}))
        self.assertEqual(resp.status_code, 200)

        # Change first name.
        resp = self.client.post(
            reverse('user', kwargs={'username': 'testuser'}),
            {'name': 'first_name', 'value': 'test name'}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            {'success': True}
        )
        user = User.objects.get(username='testuser')
        self.assertEqual(user.first_name, 'test name')

        # Change last name.
        resp = self.client.post(
            reverse('user', kwargs={'username': 'testuser'}),
            {'name': 'last_name', 'value': 'test last name'}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            {'success': True}
        )
        user = User.objects.get(username='testuser')
        self.assertEqual(user.last_name, 'test last name')

        # Change email.
        resp = self.client.post(
            reverse('user', kwargs={'username': 'testuser'}),
            {'name': 'email', 'value': 'myemail2@test.com'}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            {'success': True}
        )
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'myemail2@test.com')

        # Change palette_color_2.
        resp = self.client.post(
            reverse('user', kwargs={'username': 'testuser'}),
            {'name': 'palette_color_2', 'value': '4AF560'}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            {'success': True}
        )
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.palette_color_2, '4AF560')

        # Change timezone (fail, not valid timezone).
        resp = self.client.post(
            reverse('user', kwargs={'username': 'testuser'}),
            {'name': 'timezone', 'value': 'dummy_zone'}
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(
            str(resp.content, encoding='utf8'),
            '"This value not allowed"'
        )

        # Change timezone (success).
        resp = self.client.post(
            reverse('user', kwargs={'username': 'testuser'}),
            {'name': 'timezone', 'value': 'Europe/Kiev'}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            {'success': True}
        )
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.timezone, 'Europe/Kiev')

        # Change not existing field (fail).
        resp = self.client.post(
            reverse('user', kwargs={'username': 'testuser'}),
            {'name': 'dummy_field', 'value': 'dummy_value'}
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(
            str(resp.content, encoding='utf8'),
            '"You can\'t change this field"'
        )

        # Admin can edit any profile.
        self.client.login(username='testadmin', password='12345')
        resp = self.client.post(
            reverse('user', kwargs={'username': 'testuser'}),
            {'name': 'first_name', 'value': 'test name2'}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            {'success': True}
        )
        user = User.objects.get(username='testuser')
        self.assertEqual(user.first_name, 'test name2')

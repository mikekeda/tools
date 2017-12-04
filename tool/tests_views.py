from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Profile, Canvas


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
            {'imgBase64': sample_2,
             'slug': slug}
        )
        self.assertEqual(resp.status_code, 200)

        # Try to change not existing canvas.
        resp = self.client.post(
            reverse('canvases', kwargs={'username': 'testuser'}),
            {'imgBase64': sample_2,
             'slug': 'not-exists'}
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

    def test_views_calendar(self):
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

    def test_views_flights(self):
        resp = self.client.get(reverse('flights'))
        self.assertRedirects(resp, '/login?next=/flights')
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('flights'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'flights.html')

    def test_views_dictionary(self):
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

    def test_views_flashcards(self):
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

    def test_views_tasks(self):
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
            reverse('update_profile'),
            {'first_name': 'test1'}
        )
        self.assertRedirects(resp, '/login?next=/update-profile')
        self.client.login(username='testuser', password='12345')
        # Need to create profile for the users.
        resp = self.client.get(reverse('user',
                                       kwargs={'username': 'testuser'}))
        self.assertEqual(resp.status_code, 200)

        # Change first name.
        resp = self.client.post(
            reverse('update_profile'),
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
            reverse('update_profile'),
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
            reverse('update_profile'),
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
            reverse('update_profile'),
            {'name': 'palette_color_2', 'value': '4AF560'}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            {'success': True}
        )
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.palette_color_2, '4AF560')

        # Change timezone (fail).
        resp = self.client.post(
            reverse('update_profile'),
            {'name': 'timezone', 'value': 'dummy_zone'}
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(
            str(resp.content, encoding='utf8'),
            '"This value not allowed"'
        )

        # Change timezone (success).
        resp = self.client.post(
            reverse('update_profile'),
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
            reverse('update_profile'),
            {'name': 'dummy_field', 'value': 'dummy_value'}
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(
            str(resp.content, encoding='utf8'),
            '"You can\'t change this field"'
        )

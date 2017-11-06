from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User


class LoanedBookInstancesByUserListViewTest(TestCase):
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
    def test_home_page(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'jira-logs.html')

    def test_canvas_tool_page(self):
        resp = self.client.get('/tool/canvas')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'canvas.html')

    def test_canvas_tool_page_list(self):
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

    def test_convert_image_tool_page(self):
        resp = self.client.get('/tool/convert-image-to-base64')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'convert-image-to-base64.html')

    def test_image_info_tool_page(self):
        resp = self.client.get('/tool/get-image-exif-info')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'get-image-exif-info.html')

    def test_jira_logs_tool_page(self):
        resp = self.client.get('/tool/jira-logs')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'jira-logs.html')

    def test_text_tool_page(self):
        resp = self.client.get('/tool/text')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'text.html')

    def test_units_converter_tool_page(self):
        resp = self.client.get('/tool/units-converter')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'units-converter.html')

    # Pages available only for registered users.
    def test_calendar_page(self):
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

    def test_flights_page(self):
        resp = self.client.get(reverse('flights'))
        self.assertRedirects(resp, '/login?next=/flights')
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('flights'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'flights.html')

    def test_dictionary_page(self):
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

    def test_flashcards_page(self):
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

    def test_tasks_page(self):
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

    def test_profile_page(self):
        resp = self.client.get(reverse('user',
                                       kwargs={'username': 'testuser'}))
        self.assertRedirects(resp, '/login?next=/user/testuser')
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('user',
                                       kwargs={'username': 'testuser'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'profile.html')

    # Special pages.
    def test_login_page(self):
        resp = self.client.get(reverse('login'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'login.html')

    def test_users_page(self):
        resp = self.client.get(reverse('users'))
        self.assertRedirects(resp, '/admin/login/?next=/users')
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('users'))
        self.assertRedirects(resp, '/admin/login/?next=/users')
        self.client.login(username='testadmin', password='12345')
        resp = self.client.get(reverse('users'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'user_list.html')

    def test_sitemap_page(self):
        resp = self.client.get('/sitemap.xml')
        self.assertEqual(resp.status_code, 200)

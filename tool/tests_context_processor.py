from datetime import date

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from .context_processors import (
    categories,
    select_parent_template,
    arrival_date,
    user_profile
)
from .models import Profile


class ToolContextProcessorTest(TestCase):
    def setUp(self):
        # Create usual user.
        test_user = User.objects.create_user(username='testuser',
                                             password='12345')
        test_user.save()

    def test_context_processor_categories(self):
        result = categories()
        self.assertEqual(result, {'tools': [
            {'name': 'Canvas', 'slug': 'canvas'},
            {
                'name': 'Convert image to base64',
                'slug': 'convert-image-to-base64'
            },
            {'name': 'Get image exif info', 'slug': 'get-image-exif-info'},
            {'name': 'Text', 'slug': 'text'},
            {'name': 'Units converter', 'slug': 'units-converter'}
        ]})

    def test_context_processor_select_parent_template(self):
        resp = self.client.get(reverse('main'))
        request = resp.wsgi_request
        result = select_parent_template(request)
        self.assertEqual(result, {'parent_template': 'base.html'})

        # Ajax request.
        resp = self.client.get(
            reverse('main'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        request = resp.wsgi_request
        result = select_parent_template(request)
        self.assertEqual(result, {'parent_template': 'dummy_parent.html'})

    def test_context_processor_arrival_date(self):
        result = arrival_date()
        self.assertEqual(
            result,
            {'today': date.today(), 'arrival_date': date(2018, 2, 12)}
        )

    def test_context_processor_user_profile(self):
        # Anonymous user.
        resp = self.client.get(reverse('main'))
        request = resp.wsgi_request
        result = user_profile(request)
        self.assertEqual(result, {'profile': None})

        # Registered user.
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('main'))
        request = resp.wsgi_request
        result = user_profile(request)
        test_user = User.objects.get(username='testuser')
        profile, created = Profile.objects.get_or_create(user=test_user)
        self.assertEqual(created, False)
        self.assertEqual(result, {'profile': profile})

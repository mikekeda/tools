from django.urls import reverse

from tool.context_processors import (
    categories,
    select_parent_template,
    user_profile
)
from tool.models import Profile
from tool.tests import BaseTestCase


class ToolContextProcessorTest(BaseTestCase):
    def test_context_processor_categories(self):
        result = categories()
        self.assertEqual(result, {'tools': [
            {'name': 'Canvas', 'slug': 'canvas'},
            {'name': 'Exif info', 'slug': 'exif-info'},
            {'name': 'Image to base64', 'slug': 'image-to-base64'},
            {'name': 'Text manipulation', 'slug': 'text-manipulation'},
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
        profile, created = Profile.objects.get_or_create(user=self.test_user)
        self.assertEqual(created, False)
        self.assertEqual(result, {'profile': profile})

from django.test import TestCase

from .models import number_to_chars


class MapsViewTest(TestCase):
    def test_models_number_to_chars(self):
        result = number_to_chars(2)
        self.assertEqual(result, 'c')
        result = number_to_chars(45219)
        self.assertEqual(result, 'lVv')

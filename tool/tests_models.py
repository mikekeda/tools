import base64
from collections import namedtuple

from cryptography.fernet import Fernet

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from .models import number_to_chars, get_username_by_uid, Profile, Code, Label


class ToolModelTest(TestCase):
    def setUp(self):
        # Create usual user.
        test_user = User.objects.create_user(username='testuser',
                                             password='12345')
        test_user.save()

    def test_models_number_to_chars(self):
        result = number_to_chars(0)
        self.assertEqual(result, 'a')
        result = number_to_chars(45219)
        self.assertEqual(result, 'lVv')

    def test_get_username_by_uid(self):
        obj = namedtuple('DummyClass', ('user_id', 'user',))
        obj.user_id = 2670427
        obj.user = namedtuple('User', ('username',))
        obj.user.username = 'dummy_user'

        # Not cached.
        username = get_username_by_uid(obj)
        self.assertEqual(username, 'dummy_user')

        # Cached.
        username = get_username_by_uid(obj)
        self.assertEqual(username, 'dummy_user')

    def test_models_profile_email_password(self):
        test_user = User.objects.get(username='testuser')
        user_profile = Profile(user=test_user, email_password='testpass1')
        user_profile.save()

        self.assertEqual(str(user_profile), 'testuser')

        # Test email_password.
        key = base64.urlsafe_b64encode(
            settings.SECRET_KEY[:32].encode('utf-8')
        )
        email_password = Fernet(key).decrypt(
            user_profile.email_password.encode('utf-8')
        ).decode('utf-8')
        self.assertEqual(email_password, 'testpass1')

        # Email password wasn't changed.
        user_profile.email = 'dummy@test.me'
        user_profile.save()
        email_password = Fernet(key).decrypt(
            user_profile.email_password.encode('utf-8')
        ).decode('utf-8')
        self.assertEqual(email_password, 'testpass1')

        # Email password was changed.
        user_profile.email_password = 'testpass2'
        user_profile.save()
        email_password = Fernet(key).decrypt(
            user_profile.email_password.encode('utf-8')
        ).decode('utf-8')
        self.assertEqual(email_password, 'testpass2')

    def test_models_code(self):
        test_user = User.objects.get(username='testuser')
        Code(title='test1', text='code block 1', user=test_user).save()

        test_code = Code.objects.get(title='test1', user=test_user)
        self.assertEqual(str(test_code), 'testuser: test1')
        self.assertEqual(test_code.text, 'code block 1')
        self.assertEqual(test_code.slug[3:], number_to_chars(test_code.pk))

    def test_models_label(self):
        test_user = User.objects.get(username='testuser')
        test_label = Label(title='test1', user=test_user)
        test_label.save()
        self.assertEqual(str(test_label), 'test1')

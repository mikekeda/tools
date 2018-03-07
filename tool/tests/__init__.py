from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class BaseTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create usual user.
        cls.test_user = User.objects.create_user(username='testuser',
                                                 password='12345')
        cls.test_user.save()

        # Create admin user.
        cls.test_admin = User.objects.create_superuser(
            username='testadmin',
            email='myemail@test.com',
            password='12345'
        )
        cls.test_admin.save()

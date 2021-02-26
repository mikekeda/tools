from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class BaseTestCase(TestCase):
    test_user = None
    test_admin = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create usual user.
        cls.password = User.objects.make_random_password()
        cls.test_user = User.objects.create_user(
            username="testuser", password=cls.password
        )
        cls.test_user.save()

        # Create admin user.
        cls.test_admin = User.objects.create_superuser(
            username="testadmin",
            email="myemail@test.com",
            password=cls.password,
            first_name="Bob",
            last_name="Smit",
        )
        cls.test_admin.save()

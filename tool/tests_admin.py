from django.contrib.auth.models import User
from django.test import TestCase


class ToolAdminTest(TestCase):
    def setUp(self):
        # Create admin user.
        test_admin = User.objects.create_superuser(
            username='testadmin',
            email='myemail@test.com',
            password='12345'
        )
        test_admin.save()

    def test_admin_canvas(self):
        self.client.login(username='testadmin', password='12345')
        resp = self.client.get('/admin/tool/canvas/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/base.html')

        self.client.login(username='testadmin', password='12345')
        resp = self.client.get('/admin/tool/canvas/add/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/change_form.html')

    def test_admin_card(self):
        self.client.login(username='testadmin', password='12345')
        resp = self.client.get('/admin/tool/card/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/base.html')

        self.client.login(username='testadmin', password='12345')
        resp = self.client.get('/admin/tool/card/add/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/change_form.html')

    def test_admin_code(self):
        self.client.login(username='testadmin', password='12345')
        resp = self.client.get('/admin/tool/code/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/base.html')

        self.client.login(username='testadmin', password='12345')
        resp = self.client.get('/admin/tool/code/add/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/change_form.html')

    def test_admin_task(self):
        self.client.login(username='testadmin', password='12345')
        resp = self.client.get('/admin/tool/task/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/base.html')

        self.client.login(username='testadmin', password='12345')
        resp = self.client.get('/admin/tool/task/add/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/change_form.html')

    def test_admin_word(self):
        self.client.login(username='testadmin', password='12345')
        resp = self.client.get('/admin/tool/word/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/base.html')

        self.client.login(username='testadmin', password='12345')
        resp = self.client.get('/admin/tool/word/add/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/change_form.html')

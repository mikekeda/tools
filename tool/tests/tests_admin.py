from tool.tests import BaseTestCase


class ToolAdminTest(BaseTestCase):
    def test_admin_event(self):
        self.client.login(username='testadmin', password='12345')
        resp = self.client.get('/admin/schedule/event/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/base.html')

        resp = self.client.get('/admin/schedule/event/add/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/change_form.html')

    def test_admin_canvas(self):
        self.client.login(username='testadmin', password='12345')
        resp = self.client.get('/admin/tool/canvas/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/base.html')

        resp = self.client.get('/admin/tool/canvas/add/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/change_form.html')

    def test_admin_card(self):
        self.client.login(username='testadmin', password='12345')
        resp = self.client.get('/admin/tool/card/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/base.html')

        resp = self.client.get('/admin/tool/card/add/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/change_form.html')

    def test_admin_code(self):
        self.client.login(username='testadmin', password='12345')
        resp = self.client.get('/admin/tool/code/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/base.html')

        resp = self.client.get('/admin/tool/code/add/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/change_form.html')

    def test_admin_task(self):
        self.client.login(username='testadmin', password='12345')
        resp = self.client.get('/admin/tool/task/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/base.html')

        resp = self.client.get('/admin/tool/task/add/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/change_form.html')

    def test_admin_word(self):
        self.client.login(username='testadmin', password='12345')
        resp = self.client.get('/admin/tool/word/')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/admin/tool/word/add/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/change_form.html')

    def test_admin_label(self):
        self.client.login(username='testadmin', password='12345')
        resp = self.client.get('/admin/tool/label/')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/admin/tool/label/add/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/change_form.html')

    def test_admin_link(self):
        self.client.login(username='testadmin', password='12345')
        resp = self.client.get('/admin/tool/link/')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/admin/tool/link/add/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/change_form.html')

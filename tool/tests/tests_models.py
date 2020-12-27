from collections import namedtuple

from tool.models import Code, Label, get_username_by_uid, number_to_chars
from tool.tests import BaseTestCase


class ToolModelTest(BaseTestCase):
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

    def test_models_code(self):
        Code(title='test1', text='code block 1', user=self.test_user).save()

        test_code = Code.objects.get(title='test1', user=self.test_user)
        self.assertEqual(str(test_code), 'testuser: test1')
        self.assertEqual(test_code.text, 'code block 1')
        self.assertEqual(test_code.slug[3:], number_to_chars(test_code.pk))

        test_label1 = Label.objects.get(title='Python')
        test_label2 = Label.objects.get(title='HTML')
        test_code = Code(title='test2', text='code block 2',
                         user=self.test_user)
        test_code.save()
        test_code.labels.add(test_label1, test_label2)
        test_code.save()

        codes = Code.get_code_snippets_with_labels(self.test_user)
        for code in codes:
            self.assertTrue(code.title in ('test1', 'test2'))
            self.assertTrue(code.labels__title in ([], ['Python', 'HTML']))

    def test_models_label(self):
        test_label = Label(title='test1', user=self.test_user)
        test_label.save()
        self.assertEqual(str(test_label), 'test1')

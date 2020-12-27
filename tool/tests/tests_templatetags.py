from tool.models import Card, Task
from tool.templatetags.tool_tags import get_item, serialize
from tool.tests import BaseTestCase


class ToolTemplatetagsTest(BaseTestCase):
    def test_templatetags_get_item(self):
        # Test with dictionary.
        result = get_item({'dummy_key': 'dummy_value'}, 'dummy_key')
        self.assertEqual(result, 'dummy_value')
        result = get_item({'dummy_key': 'dummy_value'}, 'fail_key')
        self.assertEqual(result, None)

        # Test with object.
        dummy_obj = Task(title='dummy_title', description='dummy_description')
        result = get_item(dummy_obj, 'title')
        self.assertEqual(result, 'dummy_title')
        result = get_item(dummy_obj, 'description')
        self.assertEqual(result, 'dummy_description')
        result = get_item(dummy_obj, 'fail_field')
        self.assertEqual(result, None)

    def test_templatetags_serialize(self):
        dummy_obj = Card(word='dummy_word', description='dummy_description')
        dummy_obj.dummy_field = 'dummy_value'
        result = serialize(dummy_obj)
        self.assertEqual(
            result,
            '{"model": "tool.card", "pk": null, "fields": ' +
            '{"word": "dummy_word", "description": "dummy_description",' +
            ' "difficulty": "difficult", "user": null, "order": 0,' +
            ' "created_date": null, "changed_date": null}' +
            '}'
        )

from django.urls import reverse

from tool.tests import BaseTestCase


class ToolViewTest(BaseTestCase):
    def test_views_dota_draft(self):
        resp = self.client.get(reverse("tool", kwargs={"slug": "dota-draft"}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "dota-draft.html")

    def test_api_dota_prediction(self):
        resp = self.client.get(
            reverse("ml_dota_prediction") + "?team1=1,91,53,85,16&team2=122,89,75,8,72"
        )
        self.assertEqual(resp.status_code, 200)

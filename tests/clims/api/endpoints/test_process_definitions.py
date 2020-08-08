from __future__ import absolute_import

from django.core.urlresolvers import reverse

from sentry.testutils import APITestCase


class TestProcessDefinitions(APITestCase):
    def setUp(self):
        self.install_main_demo_plugin()
        self.has_context()

    def test_simple(self):
        self.toggle_log_level()
        self.login_as(self.user)
        url = reverse('clims-api-0-process-definitions')
        self.toggle_log_level()
        response = self.client.get(url)
        assert response.status_code == 200, response

        json = response.json()
        assert len(json) == 2

        for definition in json:
            assert set(definition.keys()) == {"id", "fields", "presets"}

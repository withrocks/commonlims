from __future__ import absolute_import

from django.core.urlresolvers import reverse

from sentry.testutils import APITestCase

from tests.fixtures.plugins.gemstones_inc.models import GemstoneSample


class SubstancePropertyEndpointTest(APITestCase):
    def create_gemstone(self, *args, **kwargs):
        return self.create_substance(GemstoneSample, *args, **kwargs)

    def test_find_all_substance_property(self):

        sample = self.create_gemstone(color='blue')
        sample.save()

        sample = self.create_gemstone(color='red')
        sample.save()

        sample = self.create_gemstone(color='red')
        sample.save()

        sample = self.create_gemstone(color='teal')
        sample.save()

        url = reverse('clims-api-0-substance-property',
                      kwargs={'organization_slug': sample.organization.name, 'prop': 'color'})
        self.login_as(self.user)
        response = self.client.get(url)
        assert response.status_code == 200, response.content

        assert response.data == ['blue', 'red', 'red', 'teal']

    def test_find_unique_substance_property(self):

        sample = self.create_gemstone(color='blue')
        sample.save()

        sample = self.create_gemstone(color='red')
        sample.save()

        sample = self.create_gemstone(color='red')
        sample.save()

        sample = self.create_gemstone(color='teal')
        sample.save()

        url = reverse('clims-api-0-substance-property',
                      kwargs={'organization_slug': sample.organization.name, 'prop': 'color'})

        self.login_as(self.user)
        response = self.client.get(url, {'unique': True})
        assert response.status_code == 200, response.content
        assert set(response.data) == set(['blue', 'red', 'teal'])

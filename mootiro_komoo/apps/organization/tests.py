# -*- coding: utf-8 -*-
import simplejson

from django.core.urlresolvers import reverse

from main.tests import KomooTestCase
from main.tests import logged_and_unlogged
from main.tests import A_POLYGON_GEOMETRY
from .models import Organization


def AN_ORGANIZATION_DATA():
    return {
        'name': 'IT15S',
        'description': 'Lorem ipsum.',
        'community': [1, 4],
        'link': 'http://it3s.org',
        'contact': 'Daniela e Edgar: 3456-7890',
        'target_audiences': [1, 2, 3],
        'categories': [1, 2, 3],
        'tags': 'tecnologia, sistema, desenvolvimento sustentável',
        'geometry': A_POLYGON_GEOMETRY,
    }.copy()


class OrganizationViewsTestCase(KomooTestCase):

    # new_organization
    def test_new_organization_page_is_up(self):
        self.login_user()
        self.assert_get_is_up(reverse('new_organization'))
        self.assert_ajax_is_up(reverse('new_organization'))
        self.assert_get_is_up(reverse('new_organization', args=('sao-remo',)))
        self.assert_ajax_is_up(reverse('new_organization', args=('sao-remo',)))

    def test_new_organization_creation(self):
        self.login_user()
        data = AN_ORGANIZATION_DATA()
        n0 = Organization.objects.count()
        self.client.post(reverse('new_organization'), data)
        self.assertEquals(Organization.objects.count(), n0 + 1)

    # edit_need
    def test_organization_edit_page_is_up(self):
        self.login_user()
        self.assert_get_is_up(reverse('edit_organization', args=('alavanca-brasil',)))
        self.assert_get_is_up(reverse('edit_organization', args=('sao-remo', 'alavanca-brasil')))

    def test_organization_edition(self):
        self.login_user()
        o = Organization.objects.get(slug='it3s')
        data = AN_ORGANIZATION_DATA()
        data['id'] = o.id
        url = reverse('edit_organization', kwargs=dict(organization_slug='it3s'))
        http_resp = self.client.post(url, data)
        self.assertEqual(http_resp.status_code, 200)
        o2 = Organization.objects.get(slug='it15s')
        self.assertEquals(o.id, o2.id)
        with self.assertRaises(Exception):
            Organization.objects.get(slug='it3s')

    # form validation
    def test_organization_empty_form_validation(self):
        self.login_user()
        http_resp = self.client.post(reverse('new_organization'), data={})
        json = simplejson.loads(http_resp.content)
        expected = {
            'success': 'false',
            'errors': {
                'name': ['This field is required.'],
            },
        }
        self.assertEquals(json, expected)

    # view
    @logged_and_unlogged
    def test_organization_view_page_is_up(self):
        url = reverse('view_organization', args=('alavanca-brasil',))
        self.assert_get_is_up(url)
        url = reverse('view_organization', args=('sao-remo', 'alavanca-brasil',))
        self.assert_get_is_up(url)
        url = reverse('view_organization', args=('lalala', 'alavanca-brasil',))
        self.assert_404(url)
        url = reverse('view_organization', args=('sao-remo', 'lalala',))
        self.assert_404(url)

    # list
    @logged_and_unlogged
    def test_organization_list_page_is_up(self):
        url = reverse('organization_list')
        self.assert_get_is_up(url)
        url = reverse('organization_list', args=('sao-remo',))
        self.assert_get_is_up(url)

    # searches
    @logged_and_unlogged
    def test_organization_search_by_name(self):
        url = reverse('organization_search_by_name')
        http_resp = self.client.get(url + "?term=Fomento")
        self.assertEqual(http_resp.status_code, 200)
        self.assertNotEquals(simplejson.loads(http_resp.content), [])
        http_resp = self.client.get(url + "?term=xdfg")
        self.assertEqual(http_resp.status_code, 200)
        self.assertEquals(simplejson.loads(http_resp.content), [])

    @logged_and_unlogged
    def test_organization_search_tags(self):
        url = reverse('organization_search_tags')

        http_resp = self.client.get(url + "?term=mudar")
        self.assertEqual(http_resp.status_code, 200)
        self.assertNotEquals(simplejson.loads(http_resp.content), [])

        http_resp = self.client.get(url + "?term=xwyk")
        self.assertEqual(http_resp.status_code, 200)

        # 'saúde' is a tag for need, not organization
        http_resp = self.client.get(url + "?term=saú")
        self.assertEqual(http_resp.status_code, 200)
        self.assertEquals(simplejson.loads(http_resp.content), [])

    @logged_and_unlogged
    def test_verify_org_name(self):
        url = reverse('verify_org_name')

        http_resp = self.client.post(url, dict(org_name="Minha ONG"))
        self.assertEqual(http_resp.status_code, 200)
        json = simplejson.loads(http_resp.content)
        expected = {'exists': False}
        self.assertEquals(json, expected)

        http_resp = self.client.post(url, dict(org_name="Alavanca Brasil"))
        self.assertEqual(http_resp.status_code, 200)
        json = simplejson.loads(http_resp.content)
        expected_subset = {'exists': True}
        self.assertDictContainsSubset(expected_subset, json)

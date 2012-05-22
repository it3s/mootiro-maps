# -*- coding: utf-8 -*-
import simplejson

from django.core.urlresolvers import reverse

from main.tests import KomooTestCase
from main.tests import logged_and_unlogged
from main.tests import A_POLYGON_GEOMETRY
from .models import Organization


def A_ORGANIZATION_DATA():
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
        data = A_ORGANIZATION_DATA()
        n0 = Organization.objects.count()
        self.client.post(reverse('new_organization'), data)
        self.assertEquals(Organization.objects.count(), n0 + 1)

    # edit_need
    def test_organization_edit_page_is_up(self):
        self.login_user()
        self.assert_get_is_up(reverse('edit_organization', args=('alavanca-brasil',)))
        self.assert_get_is_up(reverse('edit_organization', args=('sao-remo', 'alavanca-brasil')))

    # def test_need_edition(self):
    #     self.login_user()
    #     n = Need.objects.get(slug='coleta-de-lixo', community__slug='complexo-da-alema')
    #     print n.community.all()
    #     data = {
    #         'id': n.id,  # must set with ajax_form decorator
    #         'community': [1, 2],
    #         'title': 'Coleta de sujeira',
    #         'description': n.description,
    #         'categories': [3, 4, 5],
    #         'target_audiences': [3, 4, 5],
    #         'tags': n.tags,
    #         'geometry': str(n.geometry),
    #     }
    #     url = reverse('edit_need', args=('complexo-da-alema', 'coleta-de-lixo'))
    #     http_resp = self.client.post(url, data)
    #     self.assertEqual(http_resp.status_code, 200)
    #     n2 = Need.objects.get(slug='coleta-de-sujeira')
    #     self.assertEquals(n.id, n2.id)
    #     with self.assertRaises(Exception):
    #         Need.objects.get(slug='coleta-de-lixo')

    # # form validation
    # def test_need_empty_form_validation(self):
    #     self.login_user()
    #     http_resp = self.client.post(reverse('new_need'), data={})
    #     json = simplejson.loads(http_resp.content)
    #     expected = {
    #         'success': 'false',
    #         'errors': {
    #             'title': ['This field is required.'],
    #             'description': ['This field is required.'],
    #             'target_audiences': ['This field is required.'],
    #             'categories': ['This field is required.'],
    #         },
    #     }
    #     self.assertEquals(json, expected)

    # # view
    # @logged_and_unlogged
    # def test_need_about_page_is_up(self):
    #     url = reverse('view_need', args=('policiamento',))
    #     self.assert_get_is_up(url)
    #     url = reverse('view_need', args=('sao-remo', 'parquinho'))
    #     self.assert_get_is_up(url)

    # # list
    # @logged_and_unlogged
    # def test_communities_list_page_is_up(self):
    #     url = reverse('list_all_needs')
    #     self.assert_get_is_up(url)
    #     url = reverse('list_community_needs', args=('sao-remo',))
    #     self.assert_get_is_up(url)

    # # searches
    # @logged_and_unlogged
    # def test_need_tag_search_is_up(self):
    #     url = reverse('need_tag_search')
    #     http_resp = self.client.get(url + "?term=saú")
    #     self.assertEqual(http_resp.status_code, 200)
    #     self.assertNotEquals(simplejson.loads(http_resp.content), [])
    #     http_resp = self.client.get(url + "?term=xwyk")
    #     self.assertEqual(http_resp.status_code, 200)
    #     self.assertEquals(simplejson.loads(http_resp.content), [])

    # @logged_and_unlogged
    # def test_need_target_audience_search_is_up(self):
    #     url = reverse('target_audience_search')
    #     http_resp = self.client.get(url + "?term=crian")
    #     self.assertEqual(http_resp.status_code, 200)
    #     self.assertNotEquals(simplejson.loads(http_resp.content), [])
    #     http_resp = self.client.get(url + "?term=xwyk")
    #     self.assertEqual(http_resp.status_code, 200)
    #     self.assertEquals(simplejson.loads(http_resp.content), [])

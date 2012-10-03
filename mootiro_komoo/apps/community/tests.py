# -*- coding: utf-8 -*-
import simplejson

from django.core.urlresolvers import reverse

from main.tests import KomooTestCase, KomooUserTestCase
from main.tests import logged_and_unlogged
from main.tests import A_POLYGON_GEOMETRY
from .models import Community


def AN_UNSAVED_COMMUNITY():
    return Community(name="Anywhere", description="Lorem ipsum")


def A_COMMUNITY_DATA():
    return {
        'name': 'Vila do Tanque',
        'population': 20000,
        'description': 'Lava roupa todo dia sem perder a alegria!',
        'tags': 'sbc, prédio, condomínio',
        'geometry': A_POLYGON_GEOMETRY,
    }.copy()


class CommunitySimpleViewsTestCase(KomooUserTestCase):

    # new_community
    def test_new_community_page_is_up(self):
        self.login_user()
        self.assert_200(reverse('new_community'))
        self.assert_200(reverse('new_community'), ajax=True)

    def test_new_community_creation(self):
        self.login_user()
        data = {
            'name': 'Vila do Tanque',
            'population': 20000,
            'description': 'Lava roupa todo dia sem perder a alegria!',
            'tags': 'sbc, prédio, condomínio',
            'geometry': A_POLYGON_GEOMETRY,
        }
        self.client.post(reverse('new_community'), data)
        if not Community.objects.filter(slug='vila-do-tanque'):
            self.fail("Community was not created")

    # form validation
    def test_community_empty_form_validation(self):
        self.login_user()
        http_resp = self.client.post(reverse('new_community'), data={})
        json = simplejson.loads(http_resp.content)
        expected = {
            'success': 'false',
            'errors': {
                'name': ['This field is required.'],
                'description': ['This field is required.'],
                'geometry': ['This field is required.'],
            },
        }
        self.assertEquals(json, expected)

    def test_community_population_is_number(self):
        self.login_user()
        data = A_COMMUNITY_DATA()
        data['population'] = 'this is not a number'
        http_resp = self.client.post(reverse('new_community'), data=data)
        json = simplejson.loads(http_resp.content)
        expected = {
            'success': 'false',
            'errors': {
                'population': ['Enter a whole number.'],
            },
        }
        self.assertEquals(json, expected)

    # list
    @logged_and_unlogged
    def test_communities_list_page_is_up(self):
        url = reverse('list_communities')
        self.assert_200(url)


class CommunityViewsTestCase(KomooUserTestCase):

    fixtures = KomooUserTestCase.fixtures + ['communities.json']

    # edit_community
    def test_community_edit_page_is_up(self):
        self.login_user()
        self.assert_200(reverse('edit_community', args=(1,)))

    def test_community_edition(self):
        self.login_user()
        c = Community.objects.get(slug='sao-remo')
        data = {
            'id': c.id,  # must set with ajax_form decorator
            'name': 'Sao Removski',
            'population': c.population + 1234,
            'description': c.description,
            'tags': 'favela, usp',
            'geometry': str(c.geometry),
        }
        url = reverse('edit_community', args=(1,))
        http_resp = self.client.post(url, data)
        self.assertEqual(http_resp.status_code, 200)
        c2 = Community.objects.get(slug='sao-removski')
        self.assertEquals(c.id, c2.id)
        with self.assertRaises(Exception):
            Community.objects.get(slug='sao-remo')

    # on_map
    @logged_and_unlogged
    def test_community_on_map_page_is_up(self):
        url = reverse('community_on_map', args=(1,))
        http_resp = self.assert_200(url)
        self.assertContains(http_resp, "map-canvas-editor")

    # view
    @logged_and_unlogged
    def test_community_about_page_is_up(self):
        url = reverse('view_community', args=(1,))
        self.assert_200(url)
        url = reverse('view_community', args=(9776,))
        self.assert_404(url)

    # searches
    @logged_and_unlogged
    def test_community_search_by_name(self):
        url = reverse('search_community_by_name') + "?term=Higi"
        http_resp = self.client.get(url)
        self.assertEqual(http_resp.status_code, 200)
        self.assertNotEquals(simplejson.loads(http_resp.content), [])
        url = reverse('search_community_by_name') + "?term=xdfg"
        http_resp = self.client.get(url)
        self.assertEqual(http_resp.status_code, 200)
        self.assertEquals(simplejson.loads(http_resp.content), [])

    @logged_and_unlogged
    def test_community_search_tags(self):
        url = reverse('community_search_tags') + "?term=fave"
        http_resp = self.client.get(url)
        self.assertEqual(http_resp.status_code, 200)
        self.assertNotEquals(simplejson.loads(http_resp.content), [])
        url = reverse('community_search_tags') + "?term=xdfg"
        http_resp = self.client.get(url)
        self.assertEqual(http_resp.status_code, 200)
        self.assertEquals(simplejson.loads(http_resp.content), [])

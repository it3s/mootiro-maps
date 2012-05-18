# -*- coding: utf-8 -*-
import simplejson

from main.tests import KomooTestCase
from main.tests import logged_and_unlogged
from main.tests import A_POLYGON_GEOMETRY

from .models import Community


class CommunityViewsTestCase(KomooTestCase):

    # new_community
    def test_new_community_page_is_up(self):
        self.login_user()
        self.assert_get_is_up('/community/new')
        self.assert_ajax_is_up('/community/new')

    def test_new_community_creation(self):
        self.login_user()
        data = {
            'name': 'Vila do Tanque',
            'population': 20000,
            'description': 'Lava roupa todo dia sem perder a alegria!',
            'tags': 'sbc, prédio, condomínio',
            'geometry': A_POLYGON_GEOMETRY,
        }
        self.client.post('/community/new', data)
        if not Community.objects.filter(slug='vila-do-tanque'):
            self.fail("Community was not created")

    # edit_community
    def test_community_edit_page_is_up(self):
        self.login_user()
        self.assert_get_is_up('/sao-remo/edit')

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
        http_resp = self.client.post('/sao-remo/edit', data)
        self.assertEqual(http_resp.status_code, 200)
        c2 = Community.objects.get(slug='sao-removski')
        self.assertEquals(c.id, c2.id)
        with self.assertRaises(Exception):
            Community.objects.get(slug='sao-remo')

    # form validation
    def test_community_empty_form_validation(self):
        self.login_user()
        http_resp = self.client.post('/community/new', data={})
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

    # on_map
    @logged_and_unlogged
    def test_community_on_map_page_is_up(self):
        http_resp = self.assert_get_is_up('/sao-remo')
        self.assertContains(http_resp, "map-canvas-editor")

    # view
    @logged_and_unlogged
    def test_community_about_page_is_up(self):
        self.assert_get_is_up('/sao-remo/about')

    # list
    @logged_and_unlogged
    def test_communities_list_page_is_up(self):
        self.assert_get_is_up('/communities')

    # searches
    @logged_and_unlogged
    def test_community_search_by_name_is_up(self):
        http_resp = self.client.get('/community/search_by_name?term=Higi')
        d = simplejson.loads(http_resp.content)
        self.assertEqual(http_resp.status_code, 200)
        self.assertNotEquals(d, [])

    @logged_and_unlogged
    def test_community_search_by_tag_is_up(self):
        http_resp = self.client.get('/community/search_by_tag/?term=fave')
        self.assertEqual(http_resp.status_code, 200)
        d = simplejson.loads(http_resp.content)
        self.assertNotEquals(d, [])

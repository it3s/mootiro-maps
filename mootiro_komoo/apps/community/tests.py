# -*- coding: utf-8 -*-
from unittest import skip

from main.tests import KomooTestCase
from main.tests import logged_and_unlogged

from community.models import Community


class CommunityViewsTestCase(KomooTestCase):

    # new_community
    @skip('FIXME: Raises error on template rendering.')
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
            'geometry': '{"type":"GeometryCollection","geometries":[{"type":"Polygon","coordinates":[[[0,0],[1,1],[2,2],[0,0]]]}]}'
        }
        self.client.post('/community/new', data)
        if not Community.objects.filter(slug='vila-do-tanque'):
            self.fail("Community was not created")

    # edit_community
    def test_community_edit_page_is_up(self):
        self.login_user()
        self.assert_get_is_up('/sao-remo/edit')

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

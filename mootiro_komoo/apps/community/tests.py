# -*- coding: utf-8 -*-
from unittest import skip

from main.tests import KomooTestCase
from main.tests import logged_and_unlogged


class CommunityViewsTestCase(KomooTestCase):

    ####### community.views > view() #######
    @logged_and_unlogged
    def test_community_about_page_is_up(self):
        self.assert_get_is_up('/sao-remo/about')

    ####### community.views > on_map() #######
    @logged_and_unlogged
    def test_community_on_map_page(self):
        http_resp = self.assert_get_is_up('/sao-remo')
        self.assertContains(http_resp, "map-canvas-editor")

    ####### community.views > edit() #######
    @skip('FIXME: Raises error on template rendering.')
    def test_new_community_page_is_up(self):
        self.login_user()
        self.assert_get_is_up('/community/new')
        self.assert_ajax_is_up('/community/new')

    ####### community.views > list() #######
    @logged_and_unlogged
    def test_communities_list_page_is_up(self):
        self.assert_get_is_up('/communities')

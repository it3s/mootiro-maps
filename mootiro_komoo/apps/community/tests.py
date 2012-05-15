# -*- coding: utf-8 -*-
from main.tests import KomooTestCase


class CommunityViewsTestCase(KomooTestCase):

    def test_community_about_page_is_up(self):
        self.assert_url_is_up('/sao-remo/about')

    def test_new_community_page_is_up(self):
        self.login_user()
        self.assert_url_is_up('/need/new')

    def test_communities_list_page_is_up(self):
        self.assert_url_is_up('/communities')

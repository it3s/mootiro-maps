# -*- coding: utf-8 -*-
from django.test import TestCase


class CommunityViewsTestCase(TestCase):
    fixtures = ['test_fixtures.json']

    def test_community_about_page_is_up(self):
        http_resp = self.client.get('/sao-remo/about')
        self.assertEqual(http_resp.status_code, 200)

    def test_new_community_page_is_up(self):
        self.client.login(username="noobzin", password="testpass")
        http_resp = self.client.get('/need/new')
        self.assertEqual(http_resp.status_code, 200)

    def test_communities_list_page_is_up(self):
        http_resp = self.client.get('/communities')
        self.assertEqual(http_resp.status_code, 200)

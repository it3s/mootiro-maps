# -*- coding: utf-8 -*-
from django.test import TestCase


class CommunityViewsTestCase(TestCase):
    fixtures = ['test_fixtures.json']

    def test_community_about_page_is_up(self):
        http_resp = self.client.get('/sao-remo/about')
        self.assertEqual(http_resp.status_code, 200)

    def test_new_community_page_is_up(self):
        # FIXME: bypass CAS user atuhentication
        # https://docs.djangoproject.com/en/1.0/topics/testing/#django.test.client.Client.login
        a = self.client.login(username="tester")
        print a
        http_resp = self.client.get('/community/new')
        self.assertEqual(http_resp.status_code, 200)

    def test_communities_list_page_is_up(self):
        http_resp = self.client.get('/communities')
        self.assertEqual(http_resp.status_code, 200)

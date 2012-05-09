# -*- coding: utf-8 -*-
from django.test import TestCase


class CommunityViewsTestCase(TestCase):
    fixtures = ['test_fixtures.json']

    def test_community_about_page(self):
        http_resp = self.client.get('/sao-remo/about')
        self.assertEqual(http_resp.status_code, 200)

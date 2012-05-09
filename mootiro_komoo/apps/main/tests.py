# -*- coding: utf-8 -*-
from django.test import TestCase


class MainViewsTestCase(TestCase):
    fixtures = ['test_fixtures.json']

    def test_homepage_is_up(self):
        http_resp = self.client.get('/')
        self.assertEqual(http_resp.status_code, 200)

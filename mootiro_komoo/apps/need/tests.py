# -*- coding: utf-8 -*-
from django.test import TestCase


class NeedViewsTestCase(TestCase):
    fixtures = ['test_needs.json']

    def test_need_view_page(self):
        http_resp = self.client.get('/sao-remo/need/parquinho')
        self.assertEqual(http_resp.status_code, 200)

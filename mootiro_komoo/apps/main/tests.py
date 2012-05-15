# -*- coding: utf-8 -*-
from django.test import TestCase


class KomooTestCase(TestCase):
    fixtures = ['test_fixtures.json']

    def login_user(self, username="tester"):
        """Logs a user in assuming its password is 'testpass'. The
        test_fixtures defines two users: 'tester' and 'noobzin'."""
        self.client.login(username=username, password="testpass")

    def assert_url_is_up(self, url):
        http_resp = self.client.get(url)
        self.assertEqual(http_resp.status_code, 200)


class MainViewsTestCase(KomooTestCase):

    def test_homepage_is_up(self):
        self.assert_url_is_up('/')

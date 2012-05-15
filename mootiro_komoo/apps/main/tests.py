# -*- coding: utf-8 -*-
from django.test import TestCase
from functools import wraps


def logged_and_unlogged(test_method):
    @wraps(test_method)
    def test_wrapper(self):
        print "LOGGED run..."
        self.login_user()
        test_method(self)
        print "UNLOGGED run..."
        self.client.logout()
        test_method(self)
    return test_wrapper


class KomooTestCase(TestCase):
    fixtures = ['test_fixtures.json']

    def login_user(self, username="tester"):
        """Logs a user in assuming its password is 'testpass'. The
        test_fixtures defines two users: 'tester' and 'noobzin'."""
        self.client.login(username=username, password="testpass")

    def assert_get_is_up(self, url):
        http_resp = self.client.get(url)
        self.assertEqual(http_resp.status_code, 200)
        return http_resp

    def assert_ajax_is_up(self, url):
        http_resp = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(http_resp.status_code, 200)
        return http_resp


class MainViewsTestCase(KomooTestCase):

    def test_homepage_is_up(self):
        self.assert_get_is_up('/')

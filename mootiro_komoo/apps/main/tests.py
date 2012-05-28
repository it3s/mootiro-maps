# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from functools import wraps


A_POLYGON_GEOMETRY = '{"type":"GeometryCollection","geometries":[{"type":"Polygon","coordinates":[[[0,0],[1,1],[2,2],[0,0]]]}]}'


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
    fixtures = ['test_fixtures.json', 'contenttypes_fixtures.json']

    @classmethod
    def setUpClass(cls):
        """Called before all tests of a class"""
        # In conjunction with contenttypes_fixtures.json the command below
        # fixes content types.
        ContentType.objects.all().delete()

    def login_user(self, username="tester"):
        """Logs a user in assuming its password is 'testpass'. The
        test_fixtures defines two users: 'tester' and 'noobzin'."""
        self.client.login(username=username, password="testpass")

    def _assert_status(self, url, status, ajax=False):
        params = {}
        if ajax:
            params['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        http_resp = self.client.get(url, **params)
        self.assertEqual(http_resp.status_code, status)
        return http_resp

    def assert_200(self, url, **kw):
        return self._assert_status(url, 200, **kw)

    def assert_404(self, url, **kw):
        return self._assert_status(url, 404, **kw)


class MainViewsTestCase(KomooTestCase):

    def test_homepage_is_up(self):
        self.assert_200('/')

# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import Client
from django.contrib.contenttypes.models import ContentType
from functools import wraps

from django.contrib.auth.models import User


A_POLYGON_GEOMETRY = '''
    {
        "type":"GeometryCollection",
        "geometries":[
            {
                "type":"Polygon",
                "coordinates":[
                        [[0,0],[1,1],[2,2],[0,0]]
                ]
            }
        ]
    }
'''


def logged_and_unlogged(test_method):
    @wraps(test_method)
    def test_wrapper(self):
        try:
            self.login_user()
            test_method(self)
        except AssertionError as err:
            err.args = (err.args[0] + "\n\nLogged run failed",) + err.args[1:]
            raise
        try:
            self.client.logout()
            test_method(self)
        except Exception as err:
            err.args = (err.args[0] + "\n\nUnlogged run failed",
                    ) + err.args[1:]
            raise
    return test_wrapper


class KomooBaseTestCase(TestCase):

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


class KomooUserTestCase(KomooBaseTestCase):

    fixtures = ['users.json']
    #fixtures += ['contenttypes_fixtures.json']

    def login_user(self, username="tester"):
        """Logs a user in assuming its password is 'testpass'. The
        test_fixtures defines two users: 'tester' and 'noobzin'."""
        self.client.login(username=username, password="testpass")
        return User.objects.get(username=username)


class KomooTestCase(KomooUserTestCase):

    fixtures = KomooUserTestCase.fixtures + ['contenttypes_fixtures.json']

    @classmethod
    def setUpClass(cls):
        """Called before all tests of a class"""
        # In conjunction with contenttypes_fixtures.json the command below
        # fixes content types.
        ContentType.objects.all().delete()


class MainViewsTestCase(KomooBaseTestCase):

    def test_homepage_is_up(self):
        self.assert_200('/')

    def test_frontpage_is_up(self):
        self.assert_200('/')


#
# ================== Tests for module Utils ===================================
#


class UtilsTestCase(KomooBaseTestCase):

    def test_rest_resource_get(self):
        # this url only exists on TESTING mode
        r = Client().get('/test_resource/')
        self.assertTrue(r.status_code, 200)
        self.assertContains(r, 'Resource::GET')

    def test_rest_resource_post(self):
        r = Client().post('/test_resource/')
        self.assertTrue(r.status_code, 200)
        self.assertContains(r, 'Resource::POST')

    def test_rest_resource_put(self):
        r = Client().put('/test_resource/')
        self.assertTrue(r.status_code, 200)
        self.assertContains(r, 'Resource::PUT')

    def test_rest_resource_delete(self):
        r = Client().delete('/test_resource/')
        self.assertTrue(r.status_code, 200)
        self.assertContains(r, 'Resource::DELETE')

    def test_rest_resource_method_not_allowed(self):
        r = Client().options('/test_resource/')
        # assert method is not allowed
        self.assertTrue(r.status_code, 405)


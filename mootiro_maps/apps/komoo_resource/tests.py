# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import simplejson

from django.core.urlresolvers import reverse

from main.tests import UserTestCase, KomooTestCase
from main.tests import logged_and_unlogged
from main.tests import A_POLYGON_GEOMETRY
from .models import Resource


def AN_UNSAVED_RESOURCE():
    return Resource(name="Brasília", description="amarela")


def A_RESOURCE_DATA():
    return {
        'name': 'Ginásio de esportes',
        'description': 'Lorem ipsum.',
        'community': [1, 3],
        'contact': 'Tiozinho da segurança. Cel: 99887766.',
        'kind': 1,
        'tags': 'tecnologia, sistema, desenvolvimento sustentável',
        'geometry': A_POLYGON_GEOMETRY,
    }.copy()


class ResourceViewsSimpleWithContentTypeTestCase(KomooTestCase):

    ####### CREATION #######
    def test_new_resource_page(self):
        self.login_user()

        self.assert_200(reverse('new_resource'))
        self.assert_200(reverse('new_resource'), ajax=True)

    def test_new_resource_creation(self):
        self.login_user()
        data = A_RESOURCE_DATA()
        r0 = Resource.objects.count()
        http_resp = self.client.post(reverse('new_resource'), data)
        self.assertEquals(http_resp.status_code, 200)
        self.assertEquals(Resource.objects.count(), r0 + 1)

    ####### FORM VALIDATION #######
    def test_resource_empty_form_validation(self):
        self.login_user()
        http_resp = self.client.post(reverse('new_resource'), data={})
        json = simplejson.loads(http_resp.content)
        expected = {
            'success': 'false',
            'errors': {
                'name': ['This field is required.'],
                'description': ['This field is required.'],
            },
        }
        self.assertEquals(json, expected)

    ####### VIEW #######
    @logged_and_unlogged
    def test_organization_view_page_is_up(self):
        url = reverse('view_resource', args=('1',))
        self.assert_200(url)

        url = reverse('view_resource', args=('999',))
        self.assert_404(url)

    ####### LISTING #######
    @logged_and_unlogged
    def test_resource_list_page_is_up(self):
        url = reverse('resource_list')
        self.assert_200(url)


class ResourceViewsTestCase(UserTestCase):

    fixtures = UserTestCase.fixtures + \
        ['resources.json']

    ####### EDITION #######
    def test_resource_edit_page_is_up(self):
        self.login_user()

        kwargs = dict(id='1')
        url = reverse('edit_resource', kwargs=kwargs)
        self.assert_200(url)
        self.assert_200(url, ajax=True)

    @logged_and_unlogged
    def test_resource_search_by_kind(self):
        url = reverse('resource_search_by_kind')

        http_resp = self.client.get(url + "?term=Espaç")
        self.assertEqual(http_resp.status_code, 200)
        expected = [{'value': 1, 'label': 'Espaço'}]
        self.assertEquals(simplejson.loads(http_resp.content), expected)

        http_resp = self.client.get(url + "?term=xwyk")
        self.assertEqual(http_resp.status_code, 200)
        self.assertEquals(simplejson.loads(http_resp.content), [])


class ResourceViewsWithContentTypeTestCase(KomooTestCase):

    fixtures = KomooTestCase.fixtures + \
        ['resources.json']

    ####### EDITION #######
    def test_resource_edition(self):
        self.login_user()
        r = Resource.objects.get(id=1)
        data = A_RESOURCE_DATA()
        data['id'] = r.id
        url = reverse('edit_resource', kwargs=dict(id='1'))
        http_resp = self.client.post(url, data)
        self.assertEqual(http_resp.status_code, 200)
        r2 = Resource.objects.get(name=data["name"])
        self.assertEquals(r.id, r2.id)
        with self.assertRaises(Exception):
            Resource.objects.get(name="Quadra poliesportiva")

    ####### SEARCHES #######
    @logged_and_unlogged
    def test_resource_search_tags(self):
        url = reverse('resource_search_tags')

        http_resp = self.client.get(url + "?term=EdUcAção")
        self.assertEqual(http_resp.status_code, 200)
        self.assertEquals(simplejson.loads(http_resp.content), ['Educação'])

        http_resp = self.client.get(url + "?term=xwyk")
        self.assertEquals(simplejson.loads(http_resp.content), [])

        # 'saúde' is a tag for need, not resource
        http_resp = self.client.get(url + "?term=saú")
        self.assertEquals(simplejson.loads(http_resp.content), [])

    def test_tags_filter(self):
        from main.utils import filtered_query

        query_set = Resource.objects

        original_count = query_set.count()
        assert original_count > 0

        # Mock a request
        req = type(b'MockHttpRequest', (object,), {})

        # Test simple tag filtering with single result
        req.GET = {'filters': 'tags', 'tags': 'esporte'}
        new_query_set = filtered_query(query_set, req)
        self.assertEquals(new_query_set.count(), 1)

        # Test simple tag filtering with more than 1 result
        req.GET = {'filters': 'tags', 'tags': u'Educação'}
        new_query_set = filtered_query(query_set, req)
        self.assertEquals(new_query_set.count(), 2)

        # Test multiple (& clause) tag filtering
        req.GET = {'filters': 'tags', 'tags': u'Educação,leitura'}
        new_query_set = filtered_query(query_set, req)
        self.assertEquals(new_query_set.count(), 1)
        self.assertEquals(new_query_set[0].name, u'Biblioteca comunitária')

# -*- coding: utf-8 -*-
import simplejson

from django.core.urlresolvers import reverse

from main.tests import KomooTestCase, UserTestCase
from main.tests import logged_and_unlogged
from main.tests import A_POLYGON_GEOMETRY
from .models import Need


def AN_UNSAVED_NEED():
    return Need(title="Anywhere", description="Lorem ipsum")


def A_NEED_DATA():
    return {
        'community': 1,
        'title': 'Quadra Poliesportiva',
        'description': 'Lorem ipsum.',
        'categories': [1, 2, 3],
        'target_audiences': [1, 2, 3],
        'tags': 'esporte, futebol, quadra',
        'geometry': A_POLYGON_GEOMETRY,
    }.copy()



class NeedViewsSimpleTestCase(UserTestCase):
    # new_need
    def test_new_need_page_is_up(self):
        self.login_user()
        self.assert_200(reverse('new_need'))
        self.assert_200(reverse('new_need'), ajax=True)

    # form validation
    def test_need_empty_form_validation(self):
        self.login_user()
        http_resp = self.client.post(reverse('new_need'), data={})
        json = simplejson.loads(http_resp.content)
        expected = {
            'success': 'false',
            'errors': {
                'title': ['This field is required.'],
                'description': ['This field is required.'],
                'target_audiences': ['This field is required.'],
                'categories': ['This field is required.'],
            },
        }
        self.assertEquals(json, expected)


class NeedViewsTestCase(UserTestCase):

    fixtures = UserTestCase.fixtures + ['needs.json']

    @logged_and_unlogged
    def test_need_target_audience_search_is_up(self):
        url = reverse('target_audience_search')
        http_resp = self.client.get(url + "?term=crian")
        self.assertEqual(http_resp.status_code, 200)
        self.assertNotEquals(simplejson.loads(http_resp.content), [])
        http_resp = self.client.get(url + "?term=xwyk")
        self.assertEqual(http_resp.status_code, 200)
        self.assertEquals(simplejson.loads(http_resp.content), [])


class NeedViewsWithContentTypeTestCase(KomooTestCase):

    fixtures = KomooTestCase.fixtures + ['needs.json']

    # list
    @logged_and_unlogged
    def test_need_list_page_is_up(self):
        url = reverse('need_list')
        self.assert_200(url)

    def test_new_need_creation(self):
        self.login_user()
        data = A_NEED_DATA()
        n0 = Need.objects.count()
        self.client.post(reverse('new_need'), data)
        self.assertEquals(Need.objects.count(), n0 + 1)

    # edit_need
    def test_need_edit_page_is_up(self):
        self.login_user()
        self.assert_200(reverse('edit_need', args=(4,)))

    # view
    @logged_and_unlogged
    def test_need_view_page(self):
        url = reverse('view_need', args=(4,))
        self.assert_200(url)
        url = reverse('view_need', args=(415,))
        self.assert_404(url)


class NeedViewsWithCommunitiesTestCase(KomooTestCase):

    fixtures = KomooTestCase.fixtures + ['communities.json', 'needs.json']

    # searches
    @logged_and_unlogged
    def test_need_tag_search_is_up(self):
        url = reverse('need_tag_search')
        http_resp = self.client.get(url + "?term=saú")
        self.assertEqual(http_resp.status_code, 200)
        self.assertNotEquals(simplejson.loads(http_resp.content), [])
        http_resp = self.client.get(url + "?term=xwyk")
        self.assertEqual(http_resp.status_code, 200)
        self.assertEquals(simplejson.loads(http_resp.content), [])

    def test_need_edition(self):
        self.login_user()
        n = Need.objects.get(slug='coleta-de-lixo',
                community__slug='complexo-da-alema')
        data = {
            'id': n.id,  # must set with ajax_form decorator
            'community': [1, 2],
            'title': 'Coleta de sujeira',
            'description': n.description,
            'categories': [3, 4, 5],
            'target_audiences': [3, 4, 5],
            'tags': n.tags,
            'geometry': str(n.geometry),
        }
        url = reverse('edit_need', kwargs={'id': n.id})
        http_resp = self.client.post(url, data)
        self.assertEqual(http_resp.status_code, 200)
        n2 = Need.objects.get(slug='coleta-de-sujeira')
        self.assertEquals(n.id, n2.id)
        with self.assertRaises(Exception):
            Need.objects.get(slug='coleta-de-lixo')

    def test_need_edition_persists_m2m(self):
        # Related to Bug #2391 on redmine.
        self.login_user()

        n0 = Need.objects.get(slug='coleta-de-lixo')
        ct0 = [ct.id for ct in n0.categories.all()]
        ta0 = [ta.id for ta in n0.target_audiences.all()]

        data = {
            'id': n0.id,  # must set with ajax_form decorator
            'community': [1, 2],
            'title': n0.title,
            'description': n0.description,
            'categories': [1, 5],  # changed
            'target_audiences': [1, 5],  # changed
            'tags': n0.tags,
            'geometry': str(n0.geometry),
        }
        url = reverse('edit_need', kwargs={'id': n0.id})
        http_resp = self.client.post(url, data)
        self.assertEqual(http_resp.status_code, 200)

        n = Need.objects.get(slug='coleta-de-lixo')
        ct = [ct.id for ct in n.categories.all()]
        ta = [ta.id for ta in n.target_audiences.all()]

        self.assertNotEqual(ct0, ct)
        self.assertNotEqual(ta0, ta)

    def test_need_edition2(self):
        self.login_user()
        n = Need.objects.get(slug='coleta-de-lixo',
                             community__slug='complexo-da-alema')
        slug0 = n.slug
        id0 = n.id
        data = {
            'id': n.id,  # must set with ajax_form decorator
            'community': [1, 2],
            'title': n.title,  # does not change
            'description': n.description,
            'categories': [3, 4, 5],
            'target_audiences': [3, 4, 5],
            'geometry': str(n.geometry),
        }
        url = reverse('edit_need', kwargs={'id': n.id})
        http_resp = self.client.post(url, data)
        n = Need.objects.get(id=id0)
        self.assertEquals(n.slug, slug0)


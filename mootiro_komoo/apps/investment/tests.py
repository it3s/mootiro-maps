# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

import simplejson
import datetime

from django.core.urlresolvers import reverse

from main.tests import KomooTestCase
from main.tests import logged_and_unlogged
from main.tests import A_POLYGON_GEOMETRY
from organization.tests import AN_UNSAVED_ORGANIZATION
from .models import Investment, Investor
from organization.tests import Organization


def AN_UNSAVED_INVESTMENT():
    grantee = AN_UNSAVED_ORGANIZATION()
    grantee.save()
    investor, created = Investor.get_or_create_for(grantee)
    return Investment(title="Grana preta", description="lorem ipsum",
        date=datetime.date(2012, 12, 31), investor=investor, grantee=grantee)


def AN_INVESTMENT_DATA():
    return None
    # {
    #     'name': 'IT15S',
    #     'description': 'Lorem ipsum.',
    #     'community': [1, 4],
    #     'link': 'http://it3s.org',
    #     'contact': 'Daniela e Edgar: 3456-7890',
    #     'target_audiences': [1, 2, 3],
    #     'categories': [1, 2, 3],
    #     'tags': 'tecnologia, sistema, desenvolvimento sustentável',
    #     'geometry': A_POLYGON_GEOMETRY,
    # }.copy()


# TODO: implement tests for investment
class InvestmentViewsTestCase(KomooTestCase):

    #fixtures = KomooTestCase.fixtures + \
    #    ['communities.json', 'needs.json', 'proposals.json',
    #     'organizations.json', 'resources.json', 'investments.json']
    fixtures = KomooTestCase.fixtures + ['investments.json']

    # ####### CREATION #######
    # def test_new_resource_page(self):
    #     self.login_user()
    #     self.assert_200(reverse('new_investment', args=('higienopolis',)))

    #     self.assert_404(reverse('new_investment', args=('invalid',)))
    #     self.assert_404(reverse('new_investment', args=('invalid',)), ajax=True)

    # def test_new_resource_creation(self):
    #     self.login_user()
    #     data = A_RESOURCE_DATA()
    #     r0 = Resource.objects.count()
    #     http_resp = self.client.post(reverse('new_resource'), data)
    #     self.assertEquals(http_resp.status_code, 200)
    #     self.assertEquals(Resource.objects.count(), r0 + 1)

    # ####### EDITION #######
    # def test_resource_edit_page_is_up(self):
    #     self.login_user()

    #     kwargs = dict(id='1')
    #     url = reverse('edit_resource', kwargs=kwargs)
    #     self.assert_200(url)
    #     self.assert_200(url, ajax=True)

    # def test_resource_edition(self):
    #     self.login_user()
    #     r = Resource.objects.get(id=1)
    #     data = A_RESOURCE_DATA()
    #     data['id'] = r.id
    #     url = reverse('edit_resource', kwargs=dict(id='1'))
    #     http_resp = self.client.post(url, data)
    #     self.assertEqual(http_resp.status_code, 200)
    #     r2 = Resource.objects.get(name=data["name"])
    #     self.assertEquals(r.id, r2.id)
    #     with self.assertRaises(Exception):
    #         Resource.objects.get(name="Quadra poliesportiva")

    # ####### FORM VALIDATION #######
    # def test_resource_empty_form_validation(self):
    #     self.login_user()
    #     http_resp = self.client.post(reverse('new_resource'), data={})
    #     json = simplejson.loads(http_resp.content)
    #     expected = {
    #         'success': 'false',
    #         'errors': {
    #             'name': ['This field is required.'],
    #             'description': ['This field is required.'],
    #         },
    #     }
    #     self.assertEquals(json, expected)

    # ####### VIEW #######
    # @logged_and_unlogged
    # def test_organization_view_page_is_up(self):
    #     url = reverse('view_resource', args=('1',))
    #     self.assert_200(url)
    #     url = reverse('view_resource', args=('sao-remo', '1',))
    #     self.assert_200(url)
    #     url = reverse('view_resource', args=('parque-jurassico', '1',))
    #     self.assert_200(url)

    #     url = reverse('view_resource', args=('higienopolis', '1',))
    #     self.assert_404(url)
    #     url = reverse('view_resource', args=('999',))
    #     self.assert_404(url)
    #     url = reverse('view_resource', args=('sao-remo', '999',))
    #     self.assert_404(url)

    # ####### LISTING #######
    @logged_and_unlogged
    def test_investment_list_page_is_up(self):
        url = reverse('investment_list')
        http_resp = self.assert_200(url)
        self.assertContains(http_resp, "Investments")
        self.assertContains(http_resp, "Aluguel de sala")


    # ####### SEARCHES #######
    # @logged_and_unlogged
    # def test_resource_search_tags(self):
    #     url = reverse('resource_search_tags')

    #     http_resp = self.client.get(url + "?term=EdUcAção")
    #     self.assertEqual(http_resp.status_code, 200)
    #     self.assertEquals(simplejson.loads(http_resp.content), ['Educação'])

    #     http_resp = self.client.get(url + "?term=xwyk")
    #     self.assertEquals(simplejson.loads(http_resp.content), [])

    #     # 'saúde' is a tag for need, not resource
    #     http_resp = self.client.get(url + "?term=saú")
    #     self.assertEquals(simplejson.loads(http_resp.content), [])

    # @logged_and_unlogged
    # def test_resource_search_by_kind(self):
    #     url = reverse('resource_search_by_kind')

    #     http_resp = self.client.get(url + "?term=Espaç")
    #     self.assertEqual(http_resp.status_code, 200)
    #     expected = [{'value': 1, 'label': 'Espaço'}]
    #     self.assertEquals(simplejson.loads(http_resp.content), expected)

    #     http_resp = self.client.get(url + "?term=xwyk")
    #     self.assertEqual(http_resp.status_code, 200)
    #     self.assertEquals(simplejson.loads(http_resp.content), [])

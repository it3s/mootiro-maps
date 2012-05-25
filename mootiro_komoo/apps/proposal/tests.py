# -*- coding: utf-8 -*-
import simplejson

from django.core.urlresolvers import reverse

from main.tests import KomooTestCase
from main.tests import logged_and_unlogged
from .models import Proposal


def AN_PROPOSAL_DATA():
    return {
        'title': 'Falar com a prefeitura',
        'description': 'Lorem ipsum.',
        'number': 1,
        'need': 2,
        'cost': 10000.00,
        'report': 'Ninguém fez nada a respeito ainda.',
    }.copy()


class ProposalViewsTestCase(KomooTestCase):

    ####### CREATION #######
    def test_new_proposal_page(self):
        self.login_user()

        kwargs = dict(need_slug='parquinho')
        url = reverse('new_proposal', kwargs=kwargs)
        self.assert_200(url)
        self.assert_200(url, ajax=True)

        kwargs = dict(community_slug='sao-remo', need_slug='parquinho')
        url = reverse('new_proposal', kwargs=kwargs)
        self.assert_200(url)
        self.assert_200(url, ajax=True)

        kwargs = dict(need_slug='invalid')
        url = reverse('new_proposal', kwargs=kwargs)
        self.assert_404(url)
        self.assert_404(url, ajax=True)

        kwargs = dict(community_slug='invalid', need_slug='parquinho')
        url = reverse('new_proposal', kwargs=kwargs)
        self.assert_404(url)
        self.assert_404(url, ajax=True)

    def test_new_proposal_creation(self):
        self.login_user()

        data = AN_PROPOSAL_DATA()
        n0 = Proposal.objects.count()
        kwargs = dict(community_slug='sao-remo', need_slug='parquinho')
        url = reverse('new_proposal', kwargs=kwargs)
        self.client.post(url, data)
        self.assertEquals(Proposal.objects.count(), n0 + 1)

    ####### EDITION #######
    def test_proposal_edit_page_is_up(self):
        self.login_user()

        kwargs = dict(need_slug='alfabetizacao-de-adultos', proposal_number='1')
        url = reverse('edit_proposal', kwargs=kwargs)
        self.assert_200(url)

        kwargs = dict(community_slug='higienopolis', proposal_number='1',
            need_slug='alfabetizacao-de-adultos')
        url = reverse('edit_proposal', kwargs=kwargs)
        self.assert_200(url)

    def test_proposal_edition(self):
        self.login_user()

        p = Proposal.objects.get(need__slug='alfabetizacao-de-adultos', number=1)
        data = AN_PROPOSAL_DATA()
        data['id'] = p.id
        kwargs = dict(community_slug='higienopolis',
            need_slug='alfabetizacao-de-adultos', proposal_number='1')
        url = reverse('edit_proposal', kwargs=kwargs)
        http_resp = self.client.post(url, data)
        self.assertEqual(http_resp.status_code, 200)
        p2 = Proposal.objects.get(title=AN_PROPOSAL_DATA()['title'])
        self.assertEquals(p.id, p2.id)
        with self.assertRaises(Exception):
            Proposal.objects.get(title='Mobral')

    ####### FORM VALIDATION #######
    def test_proposal_empty_form_validation(self):
        self.login_user()

        kwargs = dict(community_slug='sao-remo', need_slug='parquinho')
        url = reverse('new_proposal', kwargs=kwargs)
        http_resp = self.client.post(url, data={})
        json = simplejson.loads(http_resp.content)
        expected = {
            'success': 'false',
            'errors': {
                'title': ['This field is required.'],
                'description': ['This field is required.'],
            },
        }
        self.assertEquals(json, expected)

    ####### VIEW #######
    @logged_and_unlogged
    def test_proposal_view_page(self):
        url = reverse('view_proposal', args=('alfabetizacao-de-adultos', '2'))
        self.assert_200(url)
        url = reverse('view_proposal', args=('higienopolis',
                'alfabetizacao-de-adultos', '2'))
        self.assert_200(url)

        url = reverse('view_proposal', args=('invalid', '2'))
        self.assert_404(url)
        url = reverse('view_proposal', args=('invalid',
                'alfabetizacao-de-adultos', '2'))
        self.assert_404(url)
        url = reverse('view_proposal', args=('alfabetizacao-de-adultos', '99'))
        self.assert_404(url)

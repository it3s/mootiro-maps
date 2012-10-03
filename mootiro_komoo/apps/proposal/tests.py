# -*- coding: utf-8 -*-
import simplejson

from django.core.urlresolvers import reverse

from main.tests import KomooUserTestCase
from main.tests import logged_and_unlogged
from need.tests import AN_UNSAVED_NEED
from .models import Proposal


def AN_UNSAVED_PROPOSAL():
    need = AN_UNSAVED_NEED()
    need.save()
    return Proposal(title="Resolver", description="lorem ipsum", need=need)


def A_PROPOSAL_DATA():
    return {
        'title': 'Falar com a prefeitura',
        'description': 'Lorem ipsum.',
        'number': 1,
        'need': 2,
        'cost': 10000.00,
        'report': 'Ninguém fez nada a respeito ainda.',
    }.copy()


class ProposalSimpleViewsTestCase(KomooUserTestCase):

    fixtures = KomooUserTestCase.fixtures + \
        ['needs.json']

    ####### CREATION #######
    def test_new_proposal_page(self):
        self.login_user()

        url = reverse('new_proposal', ) + '?need=1'
        self.assert_200(url)
        self.assert_200(url, ajax=True)

        url = reverse('new_proposal', ) + '?need=8756'
        self.assert_404(url)
        self.assert_404(url, ajax=True)

    def test_new_proposal_creation(self):
        self.login_user()

        data = A_PROPOSAL_DATA()
        n0 = Proposal.objects.count()
        url = reverse('new_proposal', ) + '?need=1'
        self.client.post(url, data)
        self.assertEquals(Proposal.objects.count(), n0 + 1)

    ####### FORM VALIDATION #######
    def test_proposal_empty_form_validation(self):
        self.login_user()
        url = reverse('new_proposal', )
        http_resp = self.client.post(url, data={'need': 1})
        json = simplejson.loads(http_resp.content)
        expected = {
            'success': 'false',
            'errors': {
                'title': ['This field is required.'],
                'description': ['This field is required.'],
            },
        }
        self.assertEquals(json, expected)



class ProposalViewsTestCase(KomooUserTestCase):

    fixtures = KomooUserTestCase.fixtures + \
        ['needs.json', 'proposals.json']

    ####### EDITION #######
    def test_proposal_edit_page_is_up(self):
        self.login_user()

        kwargs = dict(id='1')
        url = reverse('edit_proposal', kwargs=kwargs) + '?need=3'
        self.assert_200(url)

    def test_proposal_edition(self):
        self.login_user()

        p = Proposal.objects.get(need__slug='alfabetizacao-de-adultos',
                number=1)
        data = A_PROPOSAL_DATA()
        data['id'] = p.id
        kwargs = dict(id='1')
        url = reverse('edit_proposal', kwargs=kwargs) + '?need=3'
        http_resp = self.client.post(url, data)
        self.assertEqual(http_resp.status_code, 200)
        p2 = Proposal.objects.get(title=A_PROPOSAL_DATA()['title'])
        self.assertEquals(p.id, p2.id)
        with self.assertRaises(Exception):
            Proposal.objects.get(title='Mobral')

    ####### VIEW #######
    @logged_and_unlogged
    def test_proposal_view_page(self):
        url = reverse('view_proposal', kwargs={'id': 2})
        self.assert_200(url)


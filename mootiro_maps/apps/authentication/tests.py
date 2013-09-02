# -*- coding: utf-8 -*-
import unittest

from django.core.urlresolvers import reverse

from main.tests import KomooTestCase

from authentication.models import User
from signatures.models import Signature
from need.models import Need


class UserTestCase(KomooTestCase):

    fixtures = KomooTestCase.fixtures + ['needs.json']

    def test_profile_page_is_up(self):
        user = self.login_user()
        self.assert_200(reverse('user_profile', kwargs={'id': user.id}))

    def test_loads_proper_username(self):
        user = self.login_user(username='noobzin')
        response = self.client.get(reverse('user_profile', kwargs={'id': user.id}))
        self.assertContains(response, 'noobzin')

    def test_loads_signatures(self):
        need = Need.objects.get(title='Parquinho')
        user = User.objects.get(email='tester@test.com')
        Signature(user=user, content_object=need).save()
        self.login_user()
        response = self.client.get(reverse('profile_update'))
        self.assertContains(response, 'Parquinho')

    def test_new_user_page(self):
        resp = self.assert_200(reverse('user_new'))
        self.assertContains(resp, 'id_name')
        self.assertContains(resp, 'id_email')
        self.assertContains(resp, 'id_password')

    def test_external_accounts_tab_exists(self):
        user = self.login_user()
        response = self.assert_200(reverse('profile_update'))
        self.assertContains(response, 'External Accounts')

    # FIXME: seems this test is old. It does not make sense in the current
    # implementation of profile_update view
    @unittest.skip("FIXME")
    def test_change_username(self):
        id = User.objects.get(username='tester').id
        self.login_user()
        new_username = 'awesome_tester'
        self.client.post(reverse('profile_update'),
            {'username': new_username})

        user = User.objects.get(pk=id)
        self.assertEquals(user.username, new_username)

    # FIXME: seems this test is old. It does not make sense in the current
    # implementation of profile_update view
    @unittest.skip("FIXME")
    def test_change_signatures(self):
        user = User.objects.get(username='tester')
        Signature.objects.filter(user=user).delete()
        for need in Need.objects.all():
            Signature(user=user, content_object=need).save()

        self.login_user()

        signatures_count = Signature.objects.filter(user=user).count()

        assert signatures_count > 0

        signatures_list = [signature.id for signature in\
                             Signature.objects.filter(user=user)]

        self.client.post(reverse('profile_update'),
            {'username': 'tester', 'signatures': signatures_list[1:]})

        self.assertEquals(
            Signature.objects.filter(user=user).count(),
            signatures_count - 1)
        self.assertEquals(
            [sign.id for sign in Signature.objects.filter(user=user)],
            signatures_list[1:])

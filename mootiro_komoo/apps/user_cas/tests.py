# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from main.tests import KomooTestCase

from django.contrib.auth.models import User
from signatures.models import Signature
from need.models import Need


class UserCasTestCase(KomooTestCase):

    fixtures = KomooTestCase.fixtures + ['needs.json']

    def test_profile_page_is_up(self):
        self.login_user()
        self.assert_200(reverse('user_profile'))

    def test_loads_proper_username(self):
        self.login_user(username='noobzin')
        response = self.client.get(reverse('user_profile'))
        self.assertContains(response, 'noobzin')

    def test_loads_signatures(self):
        need = Need.objects.get(title='Parquinho')
        user = User.objects.get(username='tester')
        Signature(user=user, content_object=need).save()
        self.login_user()
        response = self.client.get(reverse('profile_update'))
        self.assertContains(response, 'Parquinho')

    def test_change_username(self):
        id = User.objects.get(username='tester').id
        self.login_user()
        new_username = 'awesome_tester'
        self.client.post(reverse('profile_update'),
            {'username': new_username})

        user = User.objects.get(pk=id)
        self.assertEquals(user.username, new_username)

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

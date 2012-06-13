# -*- coding: utf-8 -*-
import simplejson

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
        self.assertContains(response, 'value="noobzin"')
        self.assertContains(response, 'name="username"')

    def test_loads_signatures(self):
        need = Need.objects.get(title='Parquinho')
        user = User.objects.get(username='tester')
        Signature(user=user, content_object=need).save()
        self.login_user()
        response = self.client.get(reverse('user_profile'))
        self.assertContains(response, 'Need &gt; Parquinho')

    def test_change_username(self):
        id = User.objects.get(username='tester').id
        self.login_user()
        new_username = 'awesome_tester'
        response = self.client.post(reverse('profile_update'),
            {'username': new_username})

        user = User.objects.get(pk=id)
        self.assertEquals(user.username, new_username)

    def test_change_signatures(self):
        user = User.objects.get(username='tester')
        for need in Need.objects.filter(pk__in=[1, 2, 3]):
            Signature(user=user, content_object=need).save()
        self.login_user()
        self.client.post(reverse('profile_update'),
            {'username': 'tester', 'signatures': [2,3]})
        self.assertEquals(Signature.objects.filter(user=user).count(), 2)
        self.assertEquals(
            [sign.id for sign in Signature.objects.filter(user=user)],
            [2, 3])


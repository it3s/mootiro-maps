# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

import unittest

from .models import Update
from community.models import Community
from need.models import Need
from komoo_comments.models import Comment

from main.tests import KomooTestCase
from community.tests import A_COMMUNITY_DATA
from need.tests import A_NEED_DATA
from organization.tests import AN_ORGANIZATION_DATA
from komoo_resource.tests import A_RESOURCE_DATA
from komoo_comments.tests import A_COMMENT_DATA


class UpdateSignalsTestCase(KomooTestCase):

    fixtures = KomooTestCase.fixtures + ['communities.json', 'needs.json']

    ####### New objects #######
    def test_new_community_creates_new_update(self):
        self.login_user(username='tester')

        n0 = Update.objects.count()
        data = A_COMMUNITY_DATA()
        self.client.post(reverse('new_community'), data)
        self.assertEquals(Update.objects.count(), n0 + 1)

        last_update = Update.objects.order_by("-date")[0]
        self.assertEquals(last_update.type, Update.ADD)
        self.assertEquals(last_update.users[0], 'tester')

    def test_new_need_creates_new_update(self):
        self.login_user(username='tester')

        n0 = Update.objects.count()
        data = A_NEED_DATA()
        self.client.post(reverse('new_need'), data)
        self.assertEquals(Update.objects.count(), n0 + 1)

        last_update = Update.objects.order_by("-date")[0]
        self.assertEquals(last_update.type, Update.ADD)
        self.assertEquals(last_update.users[0], 'tester')

    @unittest.skip("Feature not implemented")
    def test_new_proposal_creates_new_update(self):
        pass

    def test_new_organization_creates_new_update(self):
        self.login_user(username='tester')

        n0 = Update.objects.count()
        data = AN_ORGANIZATION_DATA()
        self.client.post(reverse('new_organization'), data)
        self.assertEquals(Update.objects.count(), n0 + 1)

        last_update = Update.objects.order_by("-date")[0]
        self.assertEquals(last_update.type, Update.ADD)
        self.assertEquals(last_update.users[0], 'tester')

    def test_new_resource_creates_new_update(self):
        self.login_user(username='tester')

        n0 = Update.objects.count()
        data = A_RESOURCE_DATA()
        self.client.post(reverse('new_resource'), data)
        self.assertEquals(Update.objects.count(), n0 + 1)

        last_update = Update.objects.order_by("-date")[0]
        self.assertEquals(last_update.type, Update.ADD)
        self.assertEquals(last_update.users[0], 'tester')

    @unittest.skip("Feature not implemented")
    def test_new_investment_creates_new_update(self):
        pass

    ####### Objects edition #######
    def test_edition_creates_update(self):
        self.login_user(username='tester')

        n = Update.objects.count()
        data = A_COMMUNITY_DATA()
        data['id'] = 1
        self.client.post(reverse('edit_community', args=('sao-remo',)), data)
        self.assertEquals(Update.objects.count(), n + 1)

        last_update = Update.objects.order_by("-date")[0]
        self.assertEquals(last_update.type, Update.EDIT)
        self.assertEquals(last_update.users[0], 'tester')

    ####### Discussions #######
    def test_new_comment_creates_update(self):
        self.login_user(username='tester')

        n0 = Update.objects.count()
        data = A_COMMENT_DATA()
        self.client.post(reverse('comments_add'), data)
        self.assertEquals(Update.objects.count(), n0 + 1)

        last_update = Update.objects.order_by("-date")[0]
        self.assertEquals(last_update.type, Update.DISCUSSION)
        self.assertEquals(last_update.users[0], 'tester')

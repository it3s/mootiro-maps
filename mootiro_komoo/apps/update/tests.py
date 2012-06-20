# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

import unittest

from .models import Update
from community.models import Community

from main.tests import KomooTestCase
from community.tests import AN_UNSAVED_COMMUNITY, A_COMMUNITY_DATA
from need.tests import AN_UNSAVED_NEED
from proposal.tests import AN_UNSAVED_PROPOSAL
from organization.tests import AN_UNSAVED_ORGANIZATION
from komoo_resource.tests import AN_UNSAVED_RESOURCE
from investment.tests import AN_UNSAVED_INVESTMENT


class UpdateSignalsTestCase(KomooTestCase):

    fixtures = KomooTestCase.fixtures + ['communities.json']

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
        user = self.login_user()
        n0 = Update.objects.count()
        obj = AN_UNSAVED_NEED()
        obj.creator = user
        obj.save()
        self.assertEquals(Update.objects.count(), n0 + 1)

    @unittest.skip("Feature not implemented")
    def test_new_proposal_creates_new_update(self):
        user = self.login_user()
        n0 = Update.objects.count()
        obj = AN_UNSAVED_PROPOSAL()
        obj.creator = user
        obj.save()
        self.assertEquals(Update.objects.count(), n0 + 1)

    def test_new_organization_creates_new_update(self):
        user = self.login_user()
        n0 = Update.objects.count()
        obj = AN_UNSAVED_ORGANIZATION()
        obj.creator = user
        obj.save()
        self.assertEquals(Update.objects.count(), n0 + 1)

    def test_new_resource_creates_new_update(self):
        user = self.login_user()
        n0 = Update.objects.count()
        obj = AN_UNSAVED_RESOURCE()
        obj.creator = user
        obj.save()
        self.assertEquals(Update.objects.count(), n0 + 1)

    @unittest.skip("Feature not implemented")
    def test_new_investment_creates_new_update(self):
        user = self.login_user()
        n0 = Update.objects.count()
        obj = AN_UNSAVED_INVESTMENT()
        obj.creator = user
        obj.save()
        self.assertEquals(Update.objects.count(), n0 + 1)

    ####### Objects edition #######
    def test_change_community_name_creates_new_update(self):
        self.login_user()
        n0 = Update.objects.count()
        c = Community.objects.get(pk=1)
        c.description += "new description"
        c.save()
        self.assertEquals(Update.objects.count(), n0 + 1)

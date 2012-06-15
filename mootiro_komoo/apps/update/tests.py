# -*- coding: utf-8 -*-
# from django.core.urlresolvers import reverse

from .models import Update

from main.tests import KomooTestCase
from community.tests import AN_UNSAVED_COMMUNITY
from need.tests import AN_UNSAVED_NEED
from organization.tests import AN_UNSAVED_ORGANIZATION
from komoo_resource.tests import AN_UNSAVED_RESOURCE
from investment.tests import AN_UNSAVED_INVESTMENT


class UpdateSignalsTestCase(KomooTestCase):

    fixtures = KomooTestCase.fixtures

    def test_new_community_creates_new_update(self):
        user = self.login_user()
        n0 = Update.objects.count()
        obj = AN_UNSAVED_COMMUNITY()
        obj.creator = user
        obj.save()
        self.assertEquals(Update.objects.count(), n0 + 1)

    def test_new_need_creates_new_update(self):
        user = self.login_user()
        n0 = Update.objects.count()
        obj = AN_UNSAVED_NEED()
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

    def test_new_investment_creates_new_update(self):
        user = self.login_user()
        n0 = Update.objects.count()
        obj = AN_UNSAVED_INVESTMENT()
        obj.creator = user
        obj.save()
        self.assertEquals(Update.objects.count(), n0 + 1)

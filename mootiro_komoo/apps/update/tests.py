# -*- coding: utf-8 -*-
# from django.core.urlresolvers import reverse

from .models import Update

from main.tests import KomooTestCase
from community.tests import A_UNSAVED_COMMUNITY


class UpdateSignalsTestCase(KomooTestCase):

    fixtures = KomooTestCase.fixtures

    # new_community
    def test_new_community_creates_new_update(self):
        user = self.login_user()
        n0 = Update.objects.count()

        print "AAAA"
        community = A_UNSAVED_COMMUNITY()
        print "BBBB"
        community.creator = user
        print "CCCC"
        community.save()
        print "DDDD"

        self.assertEquals(Update.objects.count(), n0 + 1)

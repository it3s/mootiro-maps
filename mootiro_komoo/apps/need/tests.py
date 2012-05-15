# -*- coding: utf-8 -*-
from main.tests import KomooTestCase


class NeedViewsTestCase(KomooTestCase):

    def test_need_view_page__is_up(self):
        self.assert_get_is_up('/sao-remo/need/parquinho')

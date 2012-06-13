#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

import logging
import itertools

from annoying.decorators import render_to
from reversion.models import Version, VERSION_DELETE

logger = logging.getLogger(__name__)


@render_to("update/frontpage.html")
def frontpage(request):
    # FIXME: this is too slow!!!
    # TODO: build an updates class with its own table
    updates_number = 100
    updates = Version.objects.order_by("-revision__date_created") \
                .select_related("revision", "revision__user")

    def make_feed_dict(version):
        old = version.object_version.object
        current = version.object
        return {
            'title': unicode(old),  # use old or current?
            'user': version.revision.user,
            'date_created': version.revision.date_created,
            'object': current,
            'object_type': old._meta.verbose_name,
            'update_type': version.get_type_display().lower(),
            'update_type_id': version.type,
        }
    updates = itertools.imap(make_feed_dict, updates)

    def feed_filter(feed_dict):
        # select only addition and editions, not deletions
        if feed_dict['update_type_id'] == VERSION_DELETE:
            return False
        if feed_dict['object_type'] not in ['community', 'need',
            'organization', 'resource']:
            feed_dict['object_type']
            return False
        return True
    updates = itertools.ifilter(feed_filter, updates)

    updates = itertools.islice(updates, updates_number)

    return {'updates': updates}

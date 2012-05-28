# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import logging

import json
import datetime
from smtplib import SMTPException

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.conf import settings
from django.core.mail import mail_admins
from django.core.urlresolvers import reverse

from annoying.decorators import render_to, ajax_request

from django.db.models.loading import get_model
from moderation.models import Moderation, Report
from main.utils import (create_geojson, paginated_query, sorted_query,
                        filtered_query)

logger = logging.getLogger(__name__)


@login_required
@ajax_request
def moderation_delete(request, app_label, model_name, obj_id):
    #FIXME
    logger.debug('accessing Moderation > moderation_delete : POST={}'.format(request.POST))
    content_type = ContentType.objects.get(app_label=app_label, model=model_name)
    model = get_model(app_label, model_name)
    data_dict = {'error': _('No data')}
    if model:
        obj = get_object_or_404(model, id=obj_id)
        now = datetime.datetime.now()
        delta = now - obj.creation_date
        hours = delta.days * 24. + delta.seconds / 3600.

        if obj:
            if request.user.is_superuser or hours <= settings.DELETE_HOURS:
                # TODO
                print 'Pode deletar'
            else:
                # TODO
                print 'Precisa solicitar'
        else:
            print 'Nada para deletar???'
    return HttpResponse(json.dumps(data_dict), mimetype='application/javascript')


@render_to('moderation/report_content_box.html')
def report_content_box(request):
    logger.debug('accessing Moderation > report_context_box')
    return {}


@render_to('moderation/list.html')
def list_reports(request):
    logger.debug('accessing Moderation > list_reports')
    moderations = Moderation.objects.all()
    moderations_count = moderations.count()
    moderations = paginated_query(moderations, request)
    return {'moderations': moderations, 'moderations_count': moderations_count}


@ajax_request
def moderation_report(request, app_label, model_name, obj_id):
    logger.debug('accessing Moderation > moderation_report : POST={}'.format(request.POST))
    data_dict = {'error': _('No data'), 'success': 'false'}
    if request.method == 'POST':
        model = get_model(app_label, model_name)
        content_type = ContentType.objects.get(app_label=app_label, model=model_name)
        if model:
            obj = get_object_or_404(model, id=obj_id)
            moderation = Moderation.objects.get_for_object_or_create(obj)
            reports = Report.objects.filter(user=request.user, moderation=moderation).all()
            if reports:
                report = reports.get()
                message = _('already reported')
                success = 'true'
            else:
                reason = request.POST.get('reason', 0)
                comment = request.POST.get('comment', '')
                report = Report(moderation=moderation, reason=reason,
                        comment=comment, user=request.user)
                report.save()

                try:
                    view_url = obj.view_url
                except AttributeError:
                    view_url = 'none'
                    if hasattr(obj, 'content_object') and \
                            hasattr(obj.content_object, 'view_url'):
                        view_url = obj.content_object.view_url

                admin_url = reverse('admin:{}_{}_change'.format(app_label, model_name),
                        args=(obj.id, ))
                user = request.user
                body = _("""
Content: {0}
Content type: {1}
Content id: {2}
Content url: {3}
Admin url: {4}
Reporter: {5} (id: {6}, email: {7})
Reason: {8}
Comment: {9}
                """).format(obj, content_type, obj.id, view_url, admin_url,
                        user, user.id, user.email, report.reason_name, comment)

                try:
                    mail_admins(_('Content report'), body, fail_silently=False)
                except SMTPException:
                    pass #TODO: What?
                message = _('reported')
                success = 'true'
            data_dict = {'id': report.id, 'message': message, 'success': success}
    return HttpResponse(json.dumps(data_dict), mimetype='application/javascript')

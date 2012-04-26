# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import logging

import json
import datetime

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.conf import settings

from annoying.decorators import render_to, ajax_request

from django.db.models.loading import get_model
from moderation.models import Moderation

logger = logging.getLogger(__name__)


@login_required
@ajax_request
def moderation_delete(request, app_label, model_name, obj_id):
    logger.debug('accessing Moderation > moderation_delete : POST={}'.format(request.POST))
    content_type = ContentType.objects.get(app_label=app_label, model=model_name)
    model = get_model(app_label, model_name)
    data_dict = {'error': _('No data')}
    if model:
        obj = get_object_or_404(model, id=obj_id)
        now = datetime.datetime.now()
        delta = now - obj.creation_date
        hours = delta.days * 24. + delta.seconds / 3600.

        if hours <= settings.DELETE_HOURS:
            # TODO
            print 'Pode deletar'
        else:
            # TODO
            print 'Precisa solicitar'
    return HttpResponse(json.dumps(data_dict), mimetype='application/javascript')



@render_to('moderation/report_content_box.html')
def report_content_box(request):
    logger.debug('accessing Moderation > report_context_box')
    return dict()

@ajax_request
def moderation_report(request, app_label, model_name, obj_id):
    logger.debug('accessing Moderation > moderation_report : POST={}'.format(request.POST))
    content_type = ContentType.objects.get(app_label=app_label, model=model_name)
    data_dict = {'error': _('No data')}
    if request.method == 'POST':
        model = get_model(app_label, model_name)
        if model:
            obj = get_object_or_404(model, id=obj_id)
            reports = Moderation.objects.get_for_object(obj, user=request.user)
            if reports:
                message = _('already reported')
                report = reports[0]
            else:
                reason = request.POST.get('reason', 0)
                print reason
                comment = request.POST.get('comment', '')
                report = Moderation(content_type=content_type, object_id=obj_id,
                        content_object=obj, reason=reason, comment=comment,
                        user=request.user)
                print report
                report.save()
                message = _('reported')
            data_dict = {'id': report.id, 'message': message}
    return HttpResponse(json.dumps(data_dict), mimetype='application/javascript')

# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import logging

from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.db.models.loading import get_model

from annoying.decorators import render_to, ajax_request

from moderation.models import Moderation, Report
from main.utils import paginated_query
from moderation.utils import (can_delete, delete_object, create_report,
                              get_reports_by_user)

logger = logging.getLogger(__name__)


@ajax_request
def moderation_delete(request, app_label, model_name, obj_id):
    logger.debug('accessing Moderation > moderation_delete : POST={}'.format(
        request.POST))
    model = get_model(app_label, model_name)
    data_dict = {'error': _('No data'), 'success': 'false'}
    if model:
        obj = get_object_or_404(model, id=obj_id)

        if can_delete(obj, request.user):
            logger.debug('user can delete the content {}'.format(obj))
            confirmed = (request.POST.get('confirmed', 'false') == 'true')
            if confirmed:
                logger.debug('deletion confirmed. deleting {}'.format(obj))
                try:
                    delete_object(obj)
                    data_dict = {'next': 'showDeleteFeedback',
                                 'success': 'true'}
                except Exception, e:
                    logger.debug('An unexpected error occurred while ' \
                            'deleting {} : {}'.format(obj, e.message))
                    data_dict = {'next': 'unexpectedError',
                                 'info': e.message, 'success': 'false'}
            else:
                logger.debug('asking to display the confirmation dialog...')
                data_dict = {'next': 'confirmation', 'success': 'true'}
        else:
            requesting = (request.POST.get('action', 'none') == 'request')
            if requesting:
                comment = request.POST.get('comment', '')
                report = create_report(obj=obj, user=request.user,
                        reason=Report.DELETION_REQUEST, comment=comment)
                data_dict = {'next': 'showRequestFeedback',
                             'success': 'true'}
            else:
                logger.debug('user cannot delete the content. ' \
                        'asking to display the request dialog...')
                data_dict = {'next': 'request', 'success': 'true'}
    return data_dict


@render_to('moderation/deletion_request_box.html')
def deletion_request_box(request):
    return {}


@render_to('moderation/report_content_box.html')
def report_content_box(request):
    return {}


@render_to('moderation/list.html')
def list_reports(request):
    moderations = Moderation.objects.all()
    moderations_count = moderations.count()
    moderations = paginated_query(moderations, request)
    return {'moderations': moderations, 'moderations_count': moderations_count}


@ajax_request
def moderation_report(request, app_label, model_name, obj_id):
    logger.debug('POST={}'.format(
        request.POST))
    if request.user.is_anonymous():
        return {'message': _('Please log in first to report a content'), 'success': 'false'}
    data_dict = {'error': _('No data'), 'success': 'false'}
    if request.method == 'POST':
        model = get_model(app_label, model_name)
        if model:
            obj = get_object_or_404(model, id=obj_id)
            reports = get_reports_by_user(request.user, obj)
            if reports:
                report = reports[0]
                message = _('You\'ve already reported this content')
                success = 'true'
            else:
                reason = request.POST.get('reason', 0)
                comment = request.POST.get('comment', '')
                report = create_report(obj=obj, user=request.user,
                        reason=reason, comment=comment)

                message = _('The content was successfully reported')
                success = 'true'
            data_dict = {'id': report.id,
                         'message': message,
                         'success': success}
    return data_dict

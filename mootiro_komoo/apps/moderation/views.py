# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import logging

from smtplib import SMTPException

from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.core.mail import mail_admins
from django.core.urlresolvers import reverse
from django.db.models.loading import get_model

from annoying.decorators import render_to, ajax_request

from moderation.models import Moderation, Report
from main.utils import paginated_query
from moderation.utils import can_delete, delete_object

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
            logger.debug('user cannot delete the content. ' \
                    'asking to display the request dialog...')
            data_dict = {'next': 'request', 'success': 'true'}
    return data_dict


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
    logger.debug('accessing Moderation > moderation_report : POST={}'.format(
        request.POST))
    data_dict = {'error': _('No data'), 'success': 'false'}
    if request.method == 'POST':
        model = get_model(app_label, model_name)
        content_type = ContentType.objects.get(app_label=app_label,
                                               model=model_name)
        if model:
            obj = get_object_or_404(model, id=obj_id)
            moderation = Moderation.objects.get_for_object_or_create(obj)
            reports = Report.objects.filter(user=request.user,
                                            moderation=moderation).all()
            if reports:
                report = reports.get()
                message = _('You already reported this content! ' \
                        'Please wait while an admin verifies your report.')
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

                admin_url = reverse('admin:{}_{}_change'.format(app_label,
                                                                model_name),
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
                except SMTPException, e:
                    logger.debug('An error occurred while sending email ' \
                            'to admin : {}'.format(e))
                message = _('The content was successfully reported. An admin will verify this soon.')
                success = 'true'
            data_dict = {'id': report.id,
                         'message': message,
                         'success': success}
    return data_dict

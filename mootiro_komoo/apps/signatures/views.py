#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from annoying.decorators import ajax_request
from komoo_user.utils import login_required

from models import Signature

logger = logging.getLogger(__name__)


@ajax_request
@login_required
def follow(request):
    content_type = request.POST.get('content_type', None)
    obj_id = request.POST.get('obj', None)
    sign = request.POST.get('sign', 'true')
    if content_type and obj_id:
        if sign == 'true':
            try:
                signature, created = Signature.objects.get_or_create(
                    content_type_id=content_type,
                    object_id=obj_id,
                    user=request.user)
                success = created
            except Exception as err:
                logger.error('Erro ao criar nova assinatura: %s' % err)
                success = False
        elif sign == 'false':
            try:
                signature = Signature.objects.get(
                    content_type=content_type,
                    object_id=obj_id,
                    user=request.user)
                signature.delete()
                success = True
            except Exception as err:
                logger.error('Erro ao deletar assinatura: %s' % err)
                success = False
        else:
            success = False
    else:
        success = False
    return {'success': success}


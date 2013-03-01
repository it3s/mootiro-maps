# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
# from celery.task import task
from main.utils import send_mail_task

USER_EXPLANATIONS_MAIL_TPL = 'authentication/explanations.html'
PROJ_EXPLANATIONS_MAIL_TPL = 'project/explanations.html'


def send_explanations_mail(user, type='user'):
    if type == 'user':
        tpl = USER_EXPLANATIONS_MAIL_TPL
        title = "[MootiroMaps] Bem-vindo ao MootiroMaps"
    elif type == 'project':
        tpl = PROJ_EXPLANATIONS_MAIL_TPL
        title = "[MootiroMaps] Seu projeto foi criado"
    message = render_to_response(tpl, {'name': user.name}).content

    send_mail_task.delay(
            title=title,
            message=message,
            receivers=[user.email], html=True)



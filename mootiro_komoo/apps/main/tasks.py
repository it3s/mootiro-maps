# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from celery.task import task
from main.utils import send_mail

USER_EXPLANATIONS_MAIL_TPL = 'authentication/explanations.html'
PROJ_EXPLANATIONS_MAIL_TPL = 'project/explanations.html'


@task
def send_mail_async(title='', message='', sender='', receivers=[], html=False):
    send_mail(title=title, message=message, sender=sender,
            receivers=receivers, html=html)


def send_explanations_mail(user, type='user'):
    if type == 'user':
        tpl = USER_EXPLANATIONS_MAIL_TPL
        title = "[MootiroMaps] Bem-vindo ao MootiroMaps"
    elif type == 'project':
        tpl = PROJ_EXPLANATIONS_MAIL_TPL
        title = "[MootiroMaps] Seu projeto foi criado"
    message = render_to_response(tpl, {'name': user.name}).content

    send_mail_async.delay(
            title=title,
            message=message,
            receivers=[user.email], html=True)



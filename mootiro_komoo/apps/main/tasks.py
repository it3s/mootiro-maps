# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
# from celery.task import task
from main.utils import send_mail_task

EXPLANATIONS_MAIL_TPL = 'authentication/explanations.html'


def send_explanations_mail(user):
    message = render_to_response(EXPLANATIONS_MAIL_TPL, {'name': user.name}
              ).content

    send_mail_task.delay(
            title='Bem-vindo ao MootiroMaps',
            message=message,
            receivers=[user.email], html=True)



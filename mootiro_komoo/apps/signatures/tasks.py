# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.mail import send_mail
from celery.task import task
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from signatures.models import WeeklyDigest


@task
def send_notification_mail(obj=None, user=None):
    if obj and user:
        mail_title = "Update do Mootiro Maps"
        mail_message = """
Olá {},

O objeto "{}" que você está seguindo foi atualizado.
Visite: http://maps.mootiro.org/ para ver mais detalhes.
atenciosamente,

a equipe IT3S.
""".format(user.get_full_name() or user.username, unicode(obj))

        send_mail(
            mail_title,
            mail_message,
            'no-reply@mootiro.org',
            [user.email],
            fail_silently=False
        )


@periodic_task(run_every=crontab(minute="*/5"))
def weekly_mail_digest():
    # TODO: separar digest diario e digest semanal
    for signature in WeeklyDigest.objects.all():
        send_notification_mail(signature.content_object, signature.user)
        signature.delete()

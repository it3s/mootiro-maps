# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.mail import send_mail
from celery.task import task
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from signatures.models import Digest, DigestSignature


@task
def send_notification_mail(obj=None, user=None, mail_message=''):
    print 'sending mail: ', obj, user, mail_message
    if obj and user:
        mail_title = "Update do Mootiro Maps"
        if not mail_message:
            mail_message = """
Olá {},

O objeto "{}" que você está seguindo foi atualizado.
Visite: {} para ver mais detalhes.
atenciosamente,

a equipe IT3S.
""".format(user.get_full_name() or user.username, unicode(obj),
           'http://maps.mootiro.org' + getattr(obj, 'view_url', '/'))

        send_mail(
            mail_title,
            mail_message,
            'no-reply@mootiro.org',
            [user.email],
            fail_silently=False
        )


# @periodic_task(run_every=crontab(minute="*/2"))
# def weekly_mail_digest():
#     for signature in DigestSignature.objects.filter(digest_type='W'):
#         msg = ''
#         for content in Digest.objects.filter(digest_type='W', user=signature.user):
#             msg += "\nAtualização em {} : {}".format(
#                 content.content_object.__class__.__name__,
#                 'http://maps.mootiro.org' + getattr(content.content_object, 'view_url', '/')
#             )
#             content.delete()

#         send_notification_mail('dummy_obj', signature.user, msg)


# @periodic_task(run_every=crontab(minute="*/2"))
# def daily_mail_digest():
#     for signature in Digest.objects.filter(digest_type='D'):
#         # montar digest
#         send_notification_mail(signature.content_object, signature.user)
#         signature.delete()


# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.mail import send_mail
from celery.task import task
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from signatures.models import Digest, DigestSignature
from main.utils import komoo_permalink


@task
def send_notification_mail(obj=None, user=None, mail_message=''):
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
           'http://maps.mootiro.org' + komoo_permalink(obj)
)

        send_mail(
            mail_title,
            mail_message,
            'no-reply@mootiro.org',
            [user.email],
            fail_silently=False
        )


def periodic_mail_digest(digest_type=''):
    if digest_type:
        for signature in DigestSignature.objects.filter(digest_type=digest_type):
            user_digest = Digest.objects.filter(digest_type=digest_type, user=signature.user)
            if user_digest.count():
                msg = '''
Olá {},

Alguns objetos que você está seguindo no MootiroMaps foram atualizados:
                '''.format(signature.user.get_full_name() or signature.user.username)
                for content in user_digest:
                    msg += "\n -  Atualização em {} : {}".format(
                        content.content_object.__class__.__name__,
                        'http://maps.mootiro.org' + komoo_permalink(content.content_object)
                    )
                    content.delete()

                msg += '''\n\n

Visite-nos e veja as novidades.
atenciosamente,

a equipe IT3S.
                '''
                send_notification_mail('dummy_obj', signature.user, msg)


@periodic_task(run_every=crontab(minute=0, hour=0, day_of_week='sat'))
def weekly_mail_digest():
    periodic_mail_digest(digest_type='W')


@periodic_task(run_every=crontab(minute=0, hour=0))
def daily_mail_digest():
    periodic_mail_digest(digest_type='D')


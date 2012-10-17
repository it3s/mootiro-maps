# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from celery.task import task
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from signatures.models import Digest, DigestSignature
from main.utils import send_mail


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
""".format(user.name, unicode(obj),
           'http://maps.mootiro.org' + obj.view_url
)

        send_mail(
            mail_title,
            mail_message,
            'no-reply@mootiro.org',
            [user.email],
        )


def periodic_mail_digest(digest_type=''):
    if digest_type:
        for signature in DigestSignature.objects.filter(
                digest_type=digest_type):
            user_digest = Digest.objects.filter(digest_type=digest_type,
                                                user=signature.user)
            if user_digest.count():
                msg = '''
Olá {},

Alguns objetos que você está seguindo no MootiroMaps foram atualizados:
                '''.format(signature.user.name)
                for content in user_digest:
                    msg += "\n -  Atualização em {} : {}".format(
                        content.content_object.__class__.__name__,
                        'http://maps.mootiro.org' + content.content_object.view_url
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


# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.mail import send_mail
from celery.task import task


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
            'it3sdev@gmail.com',
            [user.email],
            fail_silently=False
        )


# from celery.task.schedules import crontab
# from celery.decorators import periodic_task

# @periodic_task(run_every=crontab(hour=7, minute=30, day_of_week=1))
# def every_monday_morning():
#     print("Execute every Monday at 7:30AM.")

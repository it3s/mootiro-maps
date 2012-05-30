# -*- coding: utf-8 -*-
from django.core.mail import send_mail
from celery.task import task


@task
def send_notification_mail(obj=None, user=None):
    if obj and user:
        send_mail(
            'Update do Mootiro Maps',
            'O objeto {} foi atualizado'.format(obj),
            'it3sdev@gmail.com',
            [user.email],
            fail_silently=False
        )


# from celery.task.schedules import crontab
# from celery.decorators import periodic_task

# @periodic_task(run_every=crontab(hour=7, minute=30, day_of_week=1))
# def every_monday_morning():
#     print("Execute every Monday at 7:30AM.")

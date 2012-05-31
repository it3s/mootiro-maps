# -*- coding: utf-8 -*-
from django.core.mail import send_mail
from celery.task import task
from django.utils.translation import ugettext_lazy as _


@task
def send_notification_mail(obj=None, user=None):
    if obj and user:
        send_mail(
            _('Mootiro Maps update'),
            _('The object "{}" which you are subscribed was updated'.format(obj)),
            'it3sdev@gmail.com',
            [user.email],
            fail_silently=False
        )


# from celery.task.schedules import crontab
# from celery.decorators import periodic_task

# @periodic_task(run_every=crontab(hour=7, minute=30, day_of_week=1))
# def every_monday_morning():
#     print("Execute every Monday at 7:30AM.")

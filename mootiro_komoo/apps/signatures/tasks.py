# -*- coding: utf-8 -*-
from celery.task import task


@task
def send_mail(obj=None):
    if obj:
        print '\n\n\nSending mail to: %s \n\n' % obj


# from celery.task.schedules import crontab
# from celery.decorators import periodic_task

# @periodic_task(run_every=crontab(hour=7, minute=30, day_of_week=1))
# def every_monday_morning():
#     print("Execute every Monday at 7:30AM.")

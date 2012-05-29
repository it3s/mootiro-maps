# -*- coding: utf-8 -*-
from celery.task import task


@task
def add(x, y):
    return x + y


# from celery.task.schedules import crontab
# from celery.decorators import periodic_task

# @periodic_task(run_every=crontab(hour=7, minute=30, day_of_week=1))
# def every_monday_morning():
#     print("Execute every Monday at 7:30AM.")

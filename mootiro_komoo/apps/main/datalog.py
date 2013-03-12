# -*_ coding: utf-8 -*-
import requests
from datetime import datetime
from django.dispatch import receiver, Signal
from django.conf import settings
from celery.task import task

from main.utils import to_json


log_data = Signal(providing_args=["object_", "user", "action"])


def _datalog_request(data, method='get'):
    return getattr(requests, method)(
        settings.DATALOG_SERVER,
        headers={'Content-Type': 'application/json'},
        data=to_json(data)
    )


@task
def datalog_request_task(data, method='get'):
    _datalog_request(data, method=method)


def get_user_updates(user, page=1, num=None):
    # fix this
    params = {
        'user': user.to_dict(),
    }
    if num:
        params['skip'] = (page - 1) * num
        params['limit'] = num

    return _datalog_request(params)


@receiver(log_data)
def log_data_receiver(sender=None, object_=None, user=None, action='', *args,
                      **kwargs):
    data = {
        'table': object_.table_ref,
        'object_id': object_.id,
        'user': user.id,
        'action': action,
        'time': datetime.now(),
        'data': to_json(object_.to_dict())
    }
    datalog_request_task.delay(data, method='post')

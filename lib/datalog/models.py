# -*- coding: utf-8 -*-
from db import Model
from utils import iso_to_datetime


def valid_action(val):
    return val in ('A', 'E', 'D')


class Datalog(Model):
    """
    Expected structure:

    {
        _id: Object ID from mongoDB
        table_name: 'name of the mootiro maps table'
        object_id: 'postgres id of the object'
        user: 'id of the user who performed the action'
        action: 'add/edit/delete'
        time: datetime for the action
        data: {
            "embeded doc for the data's current version"
        }
    }

    indexes:
    user
    table_name and object_id
    time
    """

    collection_name = 'datalog'

    structure = {
        'table': unicode,
        'object_id': int,
        'user': int,
        'action': unicode,
        'time': iso_to_datetime,
        'data': 'dynamic'
    }

    validators = {
        'action': [valid_action, ]
    }

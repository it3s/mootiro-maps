# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.parser import parse as dateutil_parse
import simplejson


def datetime_to_iso(datetime_obj):
    """ parses a python datetime object to a ISO-8601 string """
    if datetime_obj is None:
        return None
    return datetime_obj.isoformat()


def iso_to_datetime(iso_string):
    """ parses a ISO-8601 string into a python datetime object """
    if isinstance(iso_string, datetime):
        return iso_string

    if iso_string is None:
        return None
    return dateutil_parse(iso_string)


def json_to_python(json_data):
    return simplejson.loads(json_data)

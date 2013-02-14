# -*- coding=utf-8 -*-
from django.conf import settings
from pyes import ES
from pyes.queryset import generate_model

ES_INDEX = settings.ELASTICSEARCH_INDEX_NAME
ES_TYPE = 'komoo_objects'

MAPPING = {
    'object_id': {'type': 'integer'},
    'table_ref': {'type': 'string'},
    'data': {  # object
    },
}

conn = ES(settings.ELASTICSEARCH_URL)  # Use HTTP


def create_index():
    conn.indices.create_index(ES_INDEX)


def delete_index():
    conn.indices.delete_index(ES_INDEX)


def create_mapping():
    conn.indices.put_mapping(ES_TYPE, {'properties': MAPPING}, [ES_INDEX])


def get_model():
    return generate_model(ES_INDEX, ES_TYPE)


def index_object(obj):
    conn.index(obj, ES_INDEX, ES_TYPE)  # , 1)

def refreseh_index(obj):
    conn.indices.refresh(ES_INDEX)

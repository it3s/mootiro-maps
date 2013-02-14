# -*- coding=utf-8 -*-
from django.conf import settings
from pyes import ES
# from pyes.queryset import generate_model

ES_INDEX = settings.ELASTICSEARCH_INDEX_NAME
ES_TYPE = 'komoo_objects'

MAPPING = {
    "properties": {
        "object_id": {"type": "string", "analyzer": "simple"},
        "table_ref": {"type": "string", "analyzer": "simple"},
        "name": {
            "fields": {
                "name": {
                    "type": "string",
                    "analyzer": "full_name"
                },
                "partial": {
                    "type": "string",
                    "search_analyzer": "full_name",
                    "index_analyzer": "partial_name"
                }
            },
            "type": "multi_field"
        },
        # "description": {
        #     "fields": {
        #         "name": {
        #             "type": "string",
        #             "analyzer": "full_name"
        #         },
        #         "partial": {
        #             "search_analyzer": "full_name",
        #             "index_analyzer": "partial_name",
        #             "type": "string"
        #          }
        #     },
        #     "type": "multi_field"
        # }
    },
    "settings": {
        "analysis": {
            "filter": {
                "name_ngrams": {
                    "side": "front",
                    "max_gram": 10,
                    "min_gram": 2,
                    "type": "edgeNGram"
                 }
            },
            "analyzer": {
                "full_name": {
                    "filter": [
                        "standard",
                        "lowercase",
                        "asciifolding"
                    ],
                    "type": "custom",
                    "tokenizer": "standard"
                },
                "partial_name": {
                    "filter": [
                        "standard",
                        "lowercase",
                        "asciifolding",
                        "name_ngrams"
                     ],
                "type": "custom",
                "tokenizer": "standard"
              }
           }
        }
    }
}
conn = ES(settings.ELASTICSEARCH_URL)  # Use HTTP


def create_index():
    conn.indices.create_index(ES_INDEX)


def delete_index():
    conn.indices.delete_index(ES_INDEX)


def create_mapping():
    conn.indices.put_mapping(ES_TYPE, MAPPING, [ES_INDEX])


# def get_model():
#     return generate_model(ES_INDEX, ES_TYPE)


def refreseh_index(obj):
    conn.indices.refresh(ES_INDEX)


def index_object(obj):
    conn.index(obj, ES_INDEX, ES_TYPE)
    refreseh_index()

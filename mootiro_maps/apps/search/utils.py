# -*- coding=utf-8 -*-
import requests
import simplejson as json
from django.conf import settings

ES = settings.ELASTICSEARCH_URL
ES_INDEX = settings.ELASTICSEARCH_INDEX_NAME
ES_TYPE = 'komoo_objects'

MAPPINGS_DICT = {
    ES_TYPE: {
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
            "description": {
                "fields": {
                    "name": {
                        "type": "string",
                        "analyzer": "full_name"
                    },
                    "partial": {
                        "search_analyzer": "full_name",
                        "index_analyzer": "partial_name",
                        "type": "string"
                     }
                },
                "type": "multi_field"
            }
        }
    }
}


SETTINGS_DICT = {
    "settings": {
        "index": {
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
}


def search_dict(term, size=10):
    return {
        "sort": [
            "_score"
        ],
        "size": size,
        "query": {
            "filtered": {
                "query": {
                    "bool": {
                        "should": [
                            {
                                "text":{
                                    "name":{
                                        "boost":5,
                                        "query":term,
                                        "type":"phrase"
                                    }
                                }
                            },
                            {
                                "text":{
                                    "name.partial":{
                                        "boost":2,
                                        "query":term
                                    }
                                }
                            },
                            {
                                "text":{
                                    "description.partial":{
                                        "boost":1,
                                        "query":term
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
    }


table_id_map = {
    'Organization': 'o',
    'Resource': 'r',
    'Need': 'n',
    'User': 'u',
    'Community': 'c',
    'Project': 'p',
}


def es_url(url_spec, obj=None):
    if obj and isinstance(obj, dict):
        ID = obj.get('es_id', '')
    else:
        ID = ''
    return url_spec.format(ES=ES, INDEX=ES_INDEX, TYPE=ES_TYPE, ID=ID)


def reset_index():
    requests.delete(es_url('{ES}/{INDEX}'))
    requests.put(es_url('{ES}/{INDEX}/'),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(SETTINGS_DICT))


def create_mapping():
    requests.put(es_url('{ES}/{INDEX}/{TYPE}/_mapping'),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(MAPPINGS_DICT))


def refresh_index():
    requests.post(es_url('{ES}/{INDEX}]_refresh'))


def es_index_dict(obj):
    return {
        'object_id': obj.id,
        'table_ref': '{}.{}'.format(
            obj._meta.app_label, obj.__class__.__name__),
        'name': obj.name,
        'description': getattr(obj, 'description', ''),
        'es_id': '{}{}'.format(table_id_map[obj.__class__.__name__], obj.id),
    }


def index_object(obj):
    # get object_data dict or build it
    if not isinstance(obj, dict):
        object_data = es_index_dict(obj)
    else:
        object_data = {k: obj[k] for k in
                ['object_id', 'table_ref', 'name', 'description', 'es_id']}

    # get url and remove es_id from data to be saved
    url = es_url('{ES}/{INDEX}/{TYPE}/{ID}', object_data)
    if object_data.get('es_id', None):
        del object_data['es_id']

    requests.put(url,
            headers={'Content-Type': 'application/json'},
            data=json.dumps(object_data))
    # refresh_index()


def search_by_term(ter, size=10):
    r = requests.post(es_url('{ES}/{INDEX}/{TYPE}/_search'),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(search_dict(ter, size=size)))
    data = json.loads(r.content)
    hits = data.get('hits', {}).get('hits', [])
    results = []
    for hit in hits:
        res = hit['_source']
        res.update({'id': hit['_id']})
        results.append(res)
    return results

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

def search_dict(term):
    return {
   "sort":[
      "_score"
   ],
   "query":{
      "filtered":{
         "query":{
            "bool":{
               "should":[
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


def es_url(url_spec):
    return url_spec.format(ES=ES, INDEX=ES_INDEX, TYPE=ES_TYPE)


def reset_index():
    requests.delete(es_url('{ES}/{INDEX}'))
    requests.put(es_url('{ES}/{INDEX}/'),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(SETTINGS_DICT))


def create_mapping():
    requests.put(es_url('{ES}/{INDEX}/{TYPE}/_mapping'),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(MAPPINGS_DICT))


def refreseh_index():
    requests.post(es_url('{ES}/{INDEX}]_refresh'))


def index_object(obj):
    object_data = {
        'object_id': obj.id,
        'table_ref': '{}.{}'.format(
            obj._meta.app_label, obj.__class__.__name__),
        'name': obj.name,
        'description': getattr(obj, 'description', ''),
    }
    requests.post(es_url('{ES}/{INDEX}/{TYPE}'),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(object_data))
    # refresh_index()

def search_by_term(ter):
    r = requests.post(es_url('{ES}/{INDEX}/{TYPE}/_search'),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(search_dict(ter)))
    data = json.loads(r.content)
    hits = data['hits']['hits']
    return [hit['_source'] for hit in hits]

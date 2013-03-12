# -*- coding: utf-8 -*-
"""
Making requests:
    * via cUrl:

      curl -H "Content-type: application/json" -XGET http://localhost:8008 -d\
       '{
            "teste": "blaa"
        }'


    * via python requests:

      requests.get('http://localhost:8008/',
         headers={'Content-Type': 'application/json'},
         data=json.dumps({'teste': 'some stuff'}))

"""
from __future__ import unicode_literals
from flask import Blueprint, request, jsonify, current_app
from models import Datalog

app = Blueprint('main', 'main')


@app.route('/')
def retrieve_data():
    current_app.logger.debug('json:'.format(request.json))
    return jsonify({'method': 'GET'})


@app.route('/', methods=['POST'])
def add_data():
    datalog = Datalog(request.json)
    current_app.logger.debug('Datalog::{}'.format(datalog.to_dict()))
    datalog.upsert()
    return jsonify({'method': 'POST'})

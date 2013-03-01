# -*- coding:utf8 -*-

"""
Use this script to convert questions in csv
to json and put into help_center.coffee
"""

import csv
import simplejson

source = open('./help_center_questions.csv','rb')

questions = {}
for qin in csv.DictReader(source):
    if not qin['ID da ajuda']:
        continue
    elif qin['ID da ajuda'] in questions:
        print "2 questions with same ID: {}".format(qin['ID da ajuda'])
    
    qout = {}
    qout['title'] = qin['Pergunta']
    qout['body'] = qin['Resposta']

    questions[qin['ID da ajuda']] = qout

f = open('help_center_questions.json', 'w')
simplejson.dump(questions, f)
f.close()

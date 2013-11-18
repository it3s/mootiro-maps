#! /usr/bin/env python
from __future__ import unicode_literals
from authentication.models import User
import dateutil.parser
import codecs


FILE_NAME = "./scripts/migrations/v1.6.6/user_ids_and_joined_dates.txt"
DEFAULT_DATE = dateutil.parser.parse("2012-11-02 00:00:00")


def set_user_creation_date(id, date):
    try:
        user = User.objects.get(pk=id)
    except:
        user = None

    if user:
        user.creation_date = date
        user.save()
        print('User {}:{} creation_date set to {}'.format(
            user.id, user.name, date))
    else:
        print('User not found: {}'.format(id))


def set_defaults():
    for user in User.objects.all():
        user.creation_date = DEFAULT_DATE
        user.save()
        print('User {}:{} creation_date set to {}'.format(
            user.id, user.name, DEFAULT_DATE))


def fix_creation_dates():
    set_defaults()

    with codecs.open(FILE_NAME, 'r', 'utf-8') as file_:
        for line in file_:
            id, date = map(lambda x: x.strip(), line.split("|"))
            date = dateutil.parser.parse(date)
            set_user_creation_date(id, date)


fix_creation_dates()

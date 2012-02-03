#! /bin/sh
dropdb komoo && createdb -T template_postgis komoo && ./manage.py syncdb

#! /bin/sh
echo "Recreating database 'komoo'"
dropdb komoo && createdb -T template_postgis komoo
cd mootiro_komoo
./manage.py syncdb

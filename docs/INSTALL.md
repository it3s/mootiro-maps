For running this projet you need the postgis databse set up.
For more info please go to:
https://docs.djangoproject.com/en/1.3/ref/contrib/gis/install/#spatial-database

on ubuntu:
sudo apt-get install postgis libgeos-3.2.0 libgeos-c1 python-pyproj proj-bin proj-data libproj-dev proj-ps-doc libproj0 binutils
read the django docs about creating the database template.

with the database properly set:

- create a virtualenv
- activate it
- run ./scripts/boostrap.sh

OBS: our boostrap.sh and most of our instructions assumes a Ubuntu gnu/linux
machine (or any other Debian based distro), if you use a different setup
you can easily follow the script manualy making the necessary changes.
If you are on a windows machine, please jump from a bridge!

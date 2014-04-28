#!/usr/bin/env bash

# Install system dependecies
sudo apt-get install -y git nodejs npm rubygems python-dev python-pip ruby1.9.1-dev libev4 libev-dev libevent-2.0-5 libevent-dev postgresql-9.1 postgresql-9.1-postgis postgresql-server-dev-9.1 rabbitmq-server

sudo pip install fabric virtualenvwrapper
echo "
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
" >> ~/.bashrc
source ~/.bashrc

mkvirtualenv maps
workon maps

# Postgres evilness ... here be dragons!
locale-gen en_US.UTF-8
sudo sh -c "echo 'LANG=en_US.UTF-8' >> /etc/environment"
sudo sh -c "echo 'LC_ALL=en_US.UTF-8' >> /etc/environment"
sudo sh -c "echo 'LANGUAGE=\"en_US.UTF-8\"' >> /etc/default/locale"
sudo sh -c "echo 'LC_ALL=\"en_US.UTF-8\"' >> /etc/default/locale"

sudo pg_createcluster 9.1 main --start
sudo service postgresql start
sudo ln -s /tmp/.s.PGSQL.5432 /var/run/postgresql/.s.PGSQL.5432  # evil trick for pg to work properly

# Setup postgres user
sudo -u postgres createuser -r -s -d vagrant
sudo -u postgres createdb vagrant -O vagrant

# Configure MootiroMaps
if [ ! -f mootiro_maps/settings/local_settings.py ]
then
  cp mootiro_maps/settings/local_settings.py-dist mootiro_maps/settings/local_settings.py
  sed -i -e "s/'USER': 'user'/'USER': 'vagrant'/g" mootiro_maps/settings/local_settings.py
  sed -i -e "s/'PASSWORD': 'pass'/'PASSWORD': ''/g" mootiro_maps/settings/local_settings.py
fi

if [ ! -f fabfile/servers.conf ]
then
  cp fabfile/servers.conf-dist fabfile/servers.conf
  sed -i -e "s/\/PATH\/TO\/YOUR\/DEVELOPMENT_CODE/\/home\/vagrant\/mootiro-maps/g" fabfile/servers.conf
fi

# load postgis template
sh scripts/create_template_postgis.sh

sudo npm install -g coffee-script@1.2
sudo npm install -g requirejs@2.1

sudo gem install --version '~> 0.8.8' rb-inotify
sudo gem install listen
sudo gem install sass

# install and configure rabbitmq for working with celery
sudo rabbitmqctl add_user komoo komoo
sudo rabbitmqctl add_vhost mootiro_maps_mq
sudo rabbitmqctl set_permissions -p mootiro_maps_mq komoo ".*" ".*" ".*"

# Setup
echo "Creating new Mootiro Maps development environment..."
pip install -r mootiro_maps/settings/requirements.txt
pip install fabric

# install django patch
fab local install.patch

# install elasticsearch
if [ ! -d lib/elasticsearch ]
then
  fab local install.elasticsearch
fi


fab local db.create db.sync


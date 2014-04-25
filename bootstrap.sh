#!/usr/bin/env bash

if [ ! -f ~/runonce ]
then
  # Update
  apt-get update
  apt-get upgrade -y

  apt-get install -y git nodejs npm rubygems python-dev python-pip ruby1.9.1-dev libev4 libev-dev libevent-2.0-5 libevent-dev postgresql-9.1 postgresql-9.1-postgis postgresql-server-dev-9.1

  pip install fabric

  npm install -g coffee-script@1.2
  npm install -g requirejs@2.1

  gem install --version '~> 0.8.8' rb-inotify
  gem install listen
  gem install sass

  # install and configure rabbitmq for working with celery
  apt-get install rabbitmq-server -y
  rabbitmqctl add_user komoo komoo
  rabbitmqctl add_vhost mootiro_maps_mq
  rabbitmqctl set_permissions -p mootiro_maps_mq komoo ".*" ".*" ".*"


  # Link the Meppit repo
  cd /home/vagrant/
  ln -s /vagrant /home/vagrant/mootiro-maps

  # Configure MootiroMaps
  cd /home/vagrant/mootiro-maps
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

  # Setup
  cd /home/vagrant/mootiro-maps
  echo "Creating new Mootiro Maps development environment..."
  pip install -r mootiro_maps/settings/requirements.txt

  # install django patch
  patch -p0 /usr/local/lib/python2.7/dist-packages/django/contrib/gis/db/backends/postgis/adapter.py docs/postgis-adapter-2.patch

  # install elasticsearch
  if [ ! -d lib/elasticsearch ]
  then
    wget -P lib/ http://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-0.20.5.tar.gz
    tar xzvf lib/elasticsearch-0.20.5.tar.gz -C lib/
    mv lib/elasticsearch-0.20.5 lib/elasticsearch
    rm lib/elasticsearch-0.20.5.tar.gz
  fi

  locale-gen en_US.UTF-8
  echo "
LANG=en_US.UTF-8
LC_ALL=en_US.UTF-8" >> /etc/environment

  # Create postgres user
  sudo -u postgres createuser -r -s -d vagrant
  sudo -u postgres createdb vagrant -O vagrant

  cd /home/vagrant/mootiro-maps
  sudo -u vagrant sh scripts/create_template_postgis.sh

  sudo -u vagrant fab local db.create db.sync

  touch ~/runonce
fi

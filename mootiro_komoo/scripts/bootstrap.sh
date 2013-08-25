#! /usr/bin/env sh

# TODO check for npm or install nvm

# TODO check ruby / rubygems / bundler or install them

# system dependencies
# TODO check if its debian-based linux distro
sudo apt-get python-dev install libev4 libev-dev libevent-2.0-5 libevent-dev -y

# install and configure rabbitmq for working with celery
sudo apt-get install rabbitmq-server -y
sudo rabbitmqctl add_user komoo komoo
sudo rabbitmqctl add_vhost mootiro_maps_mq
sudo rabbitmqctl set_permissions -p mootiro_maps_mq komoo ".*" ".*" ".*"

# python dependencies
pip install -r settings/requirements.txt

#nodejs dependencies
npm install

# ruby dependecies
bundle install

# apply patch for django 1.3
fab build_environment

mkdir ../logs/

# run tests
fab test


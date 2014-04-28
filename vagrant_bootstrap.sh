#!/usr/bin/env bash

if [ ! -f ~/runonce ]
then
  apt-get update
  apt-get upgrade -y

  # Link the Meppit repo
  cd /home/vagrant/
  ln -s /vagrant /home/vagrant/mootiro-maps

  touch ~/runonce
fi

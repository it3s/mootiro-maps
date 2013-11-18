#! /bin/bash

VIRTUALENVWRAPPER=/etc/bash_completion.d/virtualenvwrapper

# Find out if apt-get is installed.
if [ -z `command -v apt-get` ]; then
	echo ""
	echo "This installation script requires 'apt-get' but it's not installed!"
	echo ""
	exit 1
fi

# Install virtualenvwrapper.
echo ""
echo "Installing virtualenvwrapper..."
sudo apt-get install virtualenvwrapper -y

# Asking for virtualenv name
echo ""
echo "Creating new virtualenv..."
VENVNAME=""
until [ -n "$VENVNAME" ]; do
	read -p "Enter a new virtualenv name: " VENVNAME
	if [ -z "$VENVNAME" ]; then
		echo "Virtualenv name should not be empty."
	fi
done;

# Loading virtualenvwrapper commands.
. $VIRTUALENVWRAPPER

# Creating new virtualenv
mkvirtualenv -a . $VENVNAME
workon $VENVNAME

# Installing some dependencies
echo ""
echo "Installing development dependencies..."
pip install fabric

sudo apt-get install nodejs npm rubygems python-dev ruby1.9.1-dev -y
sudo apt-get install libev4 libev-dev libevent-2.0-5 libevent-dev -y

sudo npm install -g coffee-script@1.2
sudo npm install -g requirejs@2.1

sudo gem install --version '~> 0.8.8' rb-inotify
sudo gem install listen
sudo gem install sass

echo ""
echo "Installing and configuring RabbitMQ..."
RABBITMQ_USER=""
read -i "komoo" -p "Enter a username to RabbitMQ: " RABBITMQ_USER
RABBITMQ_PASS=""
read -i "komoo" -p "Enter a password to RabbitMQ: " RABBITMQ_PASS
RABBITMQ_VHOST=""
read -i "mootiro_maps_mq" -p "Enter a vhost to RabbitMQ: " RABBITMQ_VHOST

# install and configure rabbitmq for working with celery
sudo apt-get install rabbitmq-server -y
sudo rabbitmqctl add_user $RABBITMQ_USER $RABBITMQ_PASS
sudo rabbitmqctl add_vhost $RABBITMQ_VHOST
sudo rabbitmqctl set_permissions -p $RABBITMQ_VHOST $RABBITMQ_USER ".*" ".*" ".*"

echo ""
echo "Creating new Mootiro Maps development environment..."
fab local install.dev

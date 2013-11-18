# http://maps.mootiro.org/

# Dependecies

Most dependecies are installed when you run the bootstrap.sh script.
But you still will have to handle some things:

### Python/virtualenv:

You should have a working python environment, preferrably with virtualenv.
If you are new and don't know what to do, I suggest giving a look at:

   http://github.com/yyuu/pyenv

### Ruby/Rubygems/Bundler:

You will need a working ruby env for some dependecies (we intend to
remove them on the future, but for now they are necessary).

If you don't know what to do look at rvm, its quite simple:

    http://rvm.io/

### Nodejs:

The same as with Ruby, it's necessary for now, but would be nice to remove it.
For installing a working node env with npm, take a look at:

    https://github.com/creationix/nvm

### Database:

We use Postgresql, with postgis extension. Unfortunatelly setting up postgis
isn't very easy.
If you are on a Debian-based linux distro (Ubuntu for example) you can run the
bootstrap install and the template script , everything should work.
If not, look at the django documentation about "geodjango".

### RabbitMQ:

The rabbitmq setup is handled by the bootstrap script. If you are not in a
debian-based distro, look at the script as example. Setting up Rabbitmq it's
fairly simple.

# Setup

- git clone
- activate your virtualenv
- run: scripts/bootstrap.sh
- run: scripts/create_postgis_template.sh
- run: fab create_db sync_db

# Config

    cp settings/local_settings.py-dist settings/local_settings.py

add your configurations (like DB and etc) to this file

# Runing

fab run should take care of everything

# Developing

If you are developing we have some watcher for coffeescript and sass. To use
them:

  fab work

Try to follow the conventions for each language (pep8 for python, and so on)

We work with Pull Requests, so: create a feature branch from the master,
work on it, and when it's ready open a PR. We will make a code review, and
if everything is okay, your work will be merged.


# State of things:

Unfortunatelly we have a lot of cleaning to do. So somethings are a little
bit clumsy, if you find anything weird, have sugestions, or want to help,
enter in contact with us.


# Licensing:


This project is licensed under the MIT license, read more in LICENSE.txt


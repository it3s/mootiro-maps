#! /usr/bin/env sh

command -v npm >/dev/null 2>&1 || {
    echo >&2 "NPM is required. You can install it whith:"
    echo >&2 "    curl https://raw.github.com/creationix/nvm/master/install.sh | sh ";

    echo >&2 "Remember to add nvm to your rc file, and source it."
    echo >&2 "    [[ -s ~/.nvm/nvm.sh ]] && . ~/.nvm/nvm.sh "
    echo >&2 "\nEnsure you have installed node and npm"
    exit 1;
}

command -v bundle >/dev/null 2>&1 || {
    echo >&2 "Bundler is required. You can install it whith:"
    echo >&2 "    curl -#L https://get.rvm.io | bash -s stable --autolibs=3 --ruby";
    echo >&2 "\nRemember to add rvm to your path and source it"
    echo >&2 "\nEnter the commands bellow to automatize your gemset creation/activation:"
    echo >&2 "    echo \"1.9.3\" > .ruby-version"
    echo >&2 "    echo \"mootiro_maps\" > .ruby-gemset"
    echo >&2 "    # cd again in this directory, let the magic happen."
    exit 1;
}

# system dependencies
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


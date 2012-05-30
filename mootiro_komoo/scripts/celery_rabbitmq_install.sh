sudo apt-get install rabbitmq-server -y
sudo rabbitmqctl add_user komoo komoo
sudo rabbitmqctl add_vhost mootiro_maps_mq
sudo rabbitmqctl set_permissions -p mootiro_maps_mq komoo ".*" ".*" ".*"
pip install Celery django-celery

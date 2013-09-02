#! /usr/bin/env python
# -*- coding:utf-8 -*-

from fabric.state import env
from fabric.api import task

from .run import elasticsearch as run_elasticsearch
from .base import kill_tasks, setup_django


@task
def elasticsearch():
    """ configure elasticsearch from scratch """
    run_elasticsearch(bg='true')
    env.run('sleep 10s')
    setup_django()
    from search.utils import reset_index, create_mapping
    reset_index()
    create_mapping()
    kill_tasks('elasticsearch')

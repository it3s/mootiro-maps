# -*- coding:utf-8 -*-

from fabric.api import env
env.user = 'login'  # ssh key protected

from .base import staging, production
from .service import *

from .deploy import *
from .db import *

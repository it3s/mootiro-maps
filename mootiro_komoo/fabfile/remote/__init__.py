# -*- coding:utf-8 -*-

from fabric.api import env

try:
    from .secret import *
except ImportError:
    print 'Warning: You should copy "fabfile/remote/secret.py-dist" to "fabfile/remote/secret.py" and then fill with your remote "user" and "password".'


from .base import staging, production
from .service import *

from .deploy import *
from .db import *

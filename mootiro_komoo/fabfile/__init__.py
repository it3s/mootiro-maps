from fabric.state import output

from .local_settings import *

from .old_fabfile import *
from .deploy import *


# ===== Fabric configuration ==================================================
output['debug'] = True  # see full command list


def help():
    '''Fabfile documentation'''
    local('python -c "import fabfile; help(fabfile)"')

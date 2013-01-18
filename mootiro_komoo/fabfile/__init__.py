from fabric.state import output

from .remote import *
from .old_fabfile import *


# ===== Fabric configuration ==================================================
output['debug'] = False  # see full command list


def help():
    '''Fabfile documentation'''
    local('python -c "import fabfile; help(fabfile)"')

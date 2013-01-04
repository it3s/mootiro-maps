from fabric.state import output

# from .old_fabfile import *
from .old_fabfile import run
from .remote import *


# ===== Fabric configuration ==================================================
output['debug'] = True  # see full command list


def help():
    '''Fabfile documentation'''
    local('python -c "import fabfile; help(fabfile)"')

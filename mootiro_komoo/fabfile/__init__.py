from fabric.state import output

# from .old_fabfile import *
from .remote import *
from .old_fabfile import run, shell


# ===== Fabric configuration ==================================================
output['debug'] = False  # see full command list


def help():
    '''Fabfile documentation'''
    local('python -c "import fabfile; help(fabfile)"')

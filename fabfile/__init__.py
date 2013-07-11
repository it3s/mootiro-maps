import os

from fabric.state import env, output
from fabric.api import task

import remote
from remote import use, production, staging
import local

# Gets the dir where the fabfile is. We will use it to open the config file
# if needed.
env.fabfile_dir = os.path.dirname(os.path.realpath(__file__))

# ===== Fabric configuration ==================================================
output['debug'] = False  # see full command list

@task
def help():
    '''Fabfile documentation'''
    local('python -c "import fabfile; help(fabfile)"')

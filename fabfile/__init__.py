import os

from fabric.state import env, output
from fabric.api import task, execute
from fabric.api import local as lrun

from .base import *
from .service import *
import run
import config
import db
import develop
import i18n

# ===== Utils attributes ======================================================
# Gets the dir where the fabfile is. We will use it to open the config file
# if needed.
env.fabfile_dir = os.path.dirname(os.path.realpath(__file__))

# Tasks are local by default.

# ===== Fabric configuration ==================================================
output['debug'] = False  # see full command list

@task
def local():
    '''Setup env dict for running local commands.'''
    execute(local_)

@task
def help():
    '''Fabfile documentation'''
    lrun('python -c "import fabfile; help(fabfile)"')


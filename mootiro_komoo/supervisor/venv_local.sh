#!/bin/bash
# Runs any command (the args) in the virtualenv environment where this script resides.
# You need to change the ACTIVATE_PATH variable
# depending on where your virtualenv activate file is relative to this script.
# The WORKING_DIR var controls the directory from which the command will be run.
# I put this in a bin folder at the top level of my app.
# my virtualenv structure:
# /my_env
# /my_env/bin  ( with the venv activate script )
# /my_env/my_app
# /my_env/my_app/bin/env_run.sh (this script)
# /my_en/my_app/main.py
#
# use: /path/to/env_run.sh <command>
# e.g.: /path/to/env_run.sh python main.py --arg-one --arg-two

workon komoo
exec $@

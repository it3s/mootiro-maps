Whe use Django settings by calling a specific settings file ('development.py',
'staging.py' or 'production.py'). These files first import everything from
common.py, which holds general configurations, then specializes it by type, and
finaly import the local_settings.py (which is not tracked) whith passwords
and security sensible settings.

So we have:

common.py -> development.py|staging.py|production.py -> local_settings.py
(general) ->             (specific)                  -> (security and local)

for development we maintain most tokens and other keys on development.py
But for staging and production our apis should always be placed on
local_settings (if are a project's member and need access on these
contact us).


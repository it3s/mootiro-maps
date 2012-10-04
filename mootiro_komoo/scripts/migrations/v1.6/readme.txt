some instructions:


## Removing the contrib sites and comments apps:


on the old checkout version (before git pull):

python manage.py dumpdata --exclude=sites --exclude=comments --settings=settings.settings_file > backupdb_filename.json

git pull

fab sync_all:backupdb_filename.json

another possibility is to create a pure sql migration script. (there is no one yet)


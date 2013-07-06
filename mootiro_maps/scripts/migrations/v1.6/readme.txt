some instructions:


## Removing the contrib sites and comments apps:


on the old checkout version (before git pull):

1- python manage.py dumpdata --exclude=sites --exclude=comments --settings=settings.settings_file > backupdb_filename.json

2- git pull

3- python scripts/migrations/v1.6/user_migration.py backupdb_filename.json

4- se tudo correu bem: mv temp.json backupdb_filename.json

4- fab sync_all:backupdb_filename.json

5- local_settings:
    - resetar chaves de api do facebook
    - trocar chave do google

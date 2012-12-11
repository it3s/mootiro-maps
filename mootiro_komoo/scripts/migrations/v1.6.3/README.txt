
1- CTRL+C > fab kill_manage_tasks

2- fab prod dumpdata

3- ./scripts/migration/v1.6.3/importsheet_migration.py backup_filename.json

4- se correu tudo bem, mv temp.json /backups/backup_filename-v1.6.3.json

5- git pull origin stable

6- fab sync_all:'/backups/backup_filename-v1.6.3.json'

7- fab prod run

8- vim settings/local_settings.py
    - atualizar o refresh token para ter permissão de usar o GFT

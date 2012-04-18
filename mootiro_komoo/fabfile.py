#! /usr/bin/env python
# -*- coding:utf-8 -*-

from fabric.api import *

#env.hosts = ['me@example.com:22']

# SOUTH_APP_LIST = []

django_settings = {
    'dev': '--settings=settings.development',
    'stage': '--settings=settings.staging',
    'prod': '--settings=settings.production'
}
env_ = 'dev'


def dev():
    """Set env_ironment to development"""
    global env_
    env_ = 'dev'


def stage():
    """Set env_ironment to test"""
    global env_
    env_ = 'stage'


def prod():
    """Set env_ironment to production"""
    global env_
    env_ = 'prod'


def build_environment():
    """
    build env_ironment: pip install everything + patch django for postgis
    encoding problem on postgres 9.1
    """
    local("pip install -r settings/requirements.txt")
    local("patch -p0 `which python | "
        "sed -e 's/bin\/python$/lib\/python2.7\/site-packages\/django\/contrib\/gis\/db\/backends\/postgis\/adapter.py/'` "
        "../docs/postgis-adapter-2.patch")


def run():
    """Runs django's development server"""
    if env_ == 'stage':
        local('python manage.py run_gunicorn --workers=2 --bind=127.0.0.1:8001 {}'.format(django_settings[env_]))
    else:
        local('python manage.py runserver 8001 {}'.format(django_settings[env_]))


def js_urls():
    """Creates a javascript file containing urls"""
    local('python manage.py js_urls {}'.format(django_settings[env_]))

    # remove trailing interrogations
    print 'removing trailing "?" from urls'
    import os
    s = ''
    with open(os.path.abspath(
                './apps/main/static/lib/django-js-utils/dutils.conf.urls.js'),
                'r') as f:
        s = f.read()
        s = s.replace('?', '')
    with open(os.path.abspath(
                './apps/main/static/lib/django-js-utils/dutils.conf.urls.js'),
                'w') as f:
        f.write(s)


def syncdb(create_superuser=""):
    """Runs syncdb (with no input flag by default)"""
    noinput = "" if create_superuser else "--noinput"
    local('python manage.py syncdb {} {}'.format(noinput, django_settings[env_]))
    # load_fixtures()


def recreate_db():
    """Drops komoo database, recreates it with postgis template and runs syncdb
    """
    print "Recreating database 'komoo'"
    local('dropdb mootiro_komoo && createdb -T template_postgis mootiro_komoo')


def shell():
    """Launches Django interactive shell"""
    local('python manage.py shell {}'.format(django_settings[env_]))


def load_fixtures(type_='system'):
    """
    load fixtures (system and test).
    usage:
        fab load_fixtures  ->  loads all files which name ends with '_fixtures.json'
            inside the fixtures folder (except for 'test_fixtures.json')
        fab load_fixtures:test  -> load only the fixtures/test_fixtures.json file
    """
    if type_ == 'test':
        local('python manage.py loaddata fixtures/test_fixtures.json {}'.format(
                django_settings[env_]))
    else:
        import os
        for fixture in os.listdir('fixtures'):
            if fixture.endswith('_fixtures.json') and fixture != 'test_fixtures.json':
                local('python manage.py loaddata fixtures/{} {}'.format(
                    fixture, django_settings[env_]))


def loaddata(fixture_file=None):
    """
    load a single fixture file
    usage:
        fab loaddata:fixture_file_path -> loads the given fixture file to db
    """
    if fixture_file:
        local('python manage.py loaddata {} {}'.format(
                    fixture_file, django_settings[env_]))
    else:
        print """
        Please provide a fixture file
        usage:
            fab loaddata:fixture_file_path -> loads the given fixture file to db
        """


def initial_revisions():
    """
    load initial revisions for django-revisions module
    should run only once when installed/or when loaded a new app/model
    """
    local('python manage.py createinitialrevisions {}'.format(django_settings[env_]))


def clean_media_files():
    """
    removes all media uploaded files
    """
    media_apps_list = ['upload', ]
    for app in media_apps_list:
        try:
            local('rm  -rf media/{}/'.format(app))
        except Exception as err:
            print err


def sync_all():
    """
    restart app and database from scratch.
    It: drops the DB, recreates it, syncdb, load_fixtures and call initial_revisions,
    also makes coffee and give you a hug
    """
    recreate_db()
    syncdb()
    load_fixtures()
    load_fixtures('test')
    initial_revisions()
    clean_media_files()


def dumpdata():
    """Dump DB data, for backup purposes """
    import datetime
    local('python manage.py dumpdata {} > backupdb_{}.json'.format(
        django_settings[env_],
        datetime.datetime.now().strftime('%Y_%m_%d')
        )
    )


def add_superuser(email=''):
    """
    Add superuser + staff privileges to a user, given its email
    """
    if not email:
        print 'Please provide a email addres for a valid user'
        return
    print 'Adding privileges to %s' % email

    import os
    import sys
    PROJ_DIR = os.path.abspath(os.path.dirname(__file__))
    SITE_ROOT = os.path.abspath(os.path.join(PROJ_DIR, '..'))
    sys.path.append(PROJ_DIR)
    sys.path.append(SITE_ROOT)
    from django.core.management import setup_environ
    env_name = ['', 'development', 'staging', 'production'][3*(int(env_ == 'prod')) + 2*(int(env_ == 'stage')) + (int(env_ == 'dev'))]
    environ = None
    exec 'from settings import {} as environ'.format(env_name)
    setup_environ(environ)

    from django.contrib.auth.models import User

    user = User.objects.get(email=email)

    user.is_staff = True
    user.is_superuser = True

    user.save()

    print 'success'


def fix_contenttypes():
    """ remove auto added contenttypes from django for loading data """
    import os
    import sys
    PROJ_DIR = os.path.abspath(os.path.dirname(__file__))
    SITE_ROOT = os.path.abspath(os.path.join(PROJ_DIR, '..'))
    sys.path.append(PROJ_DIR)
    sys.path.append(SITE_ROOT)
    from django.core.management import setup_environ
    env_name = ['', 'development', 'staging', 'production'][3*(int(env_ == 'prod')) + 2*(int(env_ == 'stage')) + (int(env_ == 'dev'))]
    environ = None
    exec 'from settings import {} as environ'.format(env_name)
    setup_environ(environ)

    from django.contrib.contenttypes.models import ContentType

    print 'cleaning contenttypes ... '
    ContentType.objects.all().delete()
    print '', unicode(ContentType.objects.all())

    loaddata('fixtures/contenttypes_fixtures.json')


# def get_migrated_apps():
#     """
#     Returns a list if app folowed by south.
#     Unfortunately its hard-coded because of the tables dependencies
#     """
# #    import os
# #    app_list = [f for f in os.listdir('apps') if os.path.exists(os.path.join(os.getcwd(),'apps', f,'migrations'))]
# #    return app_list
#     return SOUTH_APP_LIST


# def migrate_all(load=True):
#     """
#     Migrates all apps tracked by south
#     if the environment is dev then it load the fixtures
#     """
#     with settings(warn_only=True):
#         for app in get_migrated_apps():
#             local('python manage.py migrate {} {}'.format(app, django_settings[env_]))
#     if env_ in ['dev'] and load:
#         load_fixtures()


# def initial_migration(app):
#     """
#     Runs initial migration for a created app
#     usage: fab initial_migrate:<app_name>
#     OBS: the migrate is set to --fake. I'm assuming this will run after a syncdb,
#          if's not the case, contact me.
#     """
#     local('python manage.py schemamigration {app} --initial {env} ; python manage.py migrate {app} --fake {env}'.format(app=app, env=django_settings[env_]))


# def schemamigration(app):
#     """
#     Runs a regular a migration for a single app.
#     usage: fab schemamigration:<app_name>
#     """
#     local('python manage.py schemamigration {app} --auto {env}; python manage.py migrate {app} {env}'.format(app=app, env=django_settings[env_]))


# def full_schemamigration():
#     """
#     Runs a schemamigration for all apps
#     usage: fab full_schemamigration
#     """
#     for app in get_migrated_apps():
#         schemamigration(app)


# def full_initial_schemamigration():
#     """
#     Runs a schemamigration for all apps
#     usage: fab full_schemamigration
#     """
#     for app in get_migrated_apps():
#         initial_migration(app)


def help():
    """Fabfile documentation"""
    local('python -c "import fabfile; help(fabfile)"')

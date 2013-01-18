from fabric.api import local


def compile_coffee():
    '''Compiles coffeescript to javascript'''
    local('coffee -c static/')


def compile_sass():
    """Compiles sass to css"""
    local('sass --update ./')


def work():
    """Start watchers"""
    # compilers
    local('coffee -cw apps/ &')
    local('sass --watch ./ &')

    # test runners go here!


def test(
        apps=" ".join([
            'community', 'need', 'organization', 'proposal', 'komoo_resource',
            'investment', 'main', 'authentication', 'moderation']),
        recreate_db=False):
    """Run application tests"""
    if recreate_db:
        local('dropdb test_mootiro_komoo')
    else:
        print("Reusing old last test DB...")
    local('REUSE_DB=1 python manage.py test {} {} --verbosity=1'
            .format(apps, django_settings[env_]))


def test_js(
        apps=" ".join(['komoo_map'])):
    """Run javascript tests"""
    # TODO fix this properly
    local('phantomjs scripts/run-qunit.js static/tests/tests.html')


def shell():
    """Launches Django interactive shell"""
    local('python manage.py shell {}'.format(django_settings[env_]))


def makemessages(lang='pt_BR'):
    """create translations messages file"""
    local('python manage.py makemessages -l {} {}'.format(
        lang, django_settings[env_]))
    local('python manage.py makemessages -d djangojs -l {} {}'.format(
        lang, django_settings[env_]))


def compilemessages():
    """
    compile messages file
    """
    local('python manage.py compilemessages {}'
          .format(django_settings[env_]))

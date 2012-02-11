#!/usr/bin/env python
# -*- coding: utf-8 -*-
# http://peak.telecommunity.com/DevCenter/setuptools#developer-s-guide

import os
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(HERE, 'docs/README.rst')).read()

setup(
    name='mootiro_komoo',
    version='0.1a1',
    url='http://mootiro.org',  # 'https://github.com/it3s/komoo',
    # download_url='https://github.com/it3s/mootiro_gepeto/downloads',
    description='Web application that maps communities, ' \
        'social organizations, resources, needs and proposals for solutions',
    long_description=README,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='The IT3S team',
    author_email='team@it3s.org',
    keywords='web django social nonprofit organization resource need proposal',
    packages=find_packages(),  # (exclude=['test_project', 'test_project.*']),
    include_package_data=True,
    zip_safe=False,
    test_suite='mootiro_komoo.tests',
    install_requires=[
        'Django>=1.3',
        'geopy',
        'django-cas',  # http://code.google.com/p/django-cas/
        'django-taggit',
        'django-annoying',
        'django_tinymce',
        # 'django-comments-threaded',  # has no pypi package yet
    ],
    license='BSD license',
)

# -*- encoding: utf-8 -*- 
# @file: setup
# @author: theol
# @Date: 2018/1/2 12:39

import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r') as readme:
    README = readme.read()
new_dir = os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir))
os.chdir(new_dir)

setup(
        name='focusonecc-common',
        version='0.1',
        package_dir={'common': ''},
        packages=[
            'common',
            'common.auth',
            'common.commands',
            'common.demo',
            'common.fabrics',
            'common.factories',
            'common.geo',
            'common.models',
            'common.notification',
            'common.notification.services',
            'common.notification.services.umessage',
            'common.payment',
            'common.resources',
            'common.templatetags',
            'common.tests',
            'common.utils',
            'common.validators',
            'common.widgets'
        ],

        include_package_data=True,
        license='MIT License',
        description='Django backend common application',
        long_description=README,
        url='http://github.com/focusonecc/common',
        author_email='theol.liang@foxmail.com',
        classifiers=[
            'Environment :: Web Environment',
            'Framework :: Django',
            'Intended Audience :: Developers',
            'Operation System :: OI Independent',
            'Programming Language :: Python',
        ]

)

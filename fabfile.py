# -*- coding: utf-8 -*-
# @Author: theo-l
# @Date:   2017-07-05 11:41:52
# @Last Modified by:   theo-l
# @Last Modified time: 2017-07-05 12:09:46

"""
A demo for the fabrics tool
"""

from fabric.api import (env, task, hosts)
from fabrics import HostConfig, DebRequirement, PyRequirement

# Remote host general configurations
HOST_CONFIG = [
    ('vagrant@192.168.33.10:22', 'vagrant', 'dev', 'dev')
]

# Remote host OS dependencies configurations
OS_REQUIREMENTS = (
    'nginx',
    'git',
    'python-dev',
    'python3-dev'
)

# Remote host Python environment configurations
PY_REQUIREMENTS = (
    'Django==1.10',
    'requests==2.8.0'
)

host_config = HostConfig(host_config=HOST_CONFIG)
host_config.setup_fabric_env(env)

deb = DebRequirement(requirements=OS_REQUIREMENTS)
py = PyRequirement(requirements=PY_REQUIREMENTS)


def setUp():
    """
    Initiate the remove host environment
    """
    deb.install_requirements()
    py.install_requirements()


def reset():
    """
    Initiate the remove host environment
    """
    deb.uninstall_requirements()
    py.uninstall_requirements()


############################################################
# setUp remote hosts
############################################################
@task
@hosts(host_config.DEV_HOSTS)
def setup_dev():
    setUp()


@task
@hosts(host_config.ALL_HOSTS)
def setup_all():
    setUp()


############################################################
# Reset remote hosts
############################################################
@task
@hosts(host_config.DEV_HOSTS)
def reset_dev():
    reset()


@task
@hosts(host_config.ALL_HOSTS)
def reset_all():
    reset()

# -*- encoding: utf-8 -*-

import os
import platform
import six
from fabric.api import run, cd
from subprocess import call


class BaseRequirement:
    def __init__(self):
        pass

    def install_requirements(self, name=None):
        pass

    def upgrade_requirements(self, name=None):
        pass

    def uninstall_requirements(self, name=None):
        pass


class OSRequirement(BaseRequirement):
    pass


class PyRequirement(BaseRequirement):
    pass

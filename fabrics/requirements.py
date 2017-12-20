# -*- coding: utf-8 -*-
# @Author: theo-l
# @Date:   2017-07-05 11:11:28
# @Last Modified by:   theo-l
# @Last Modified time: 2017-07-05 12:28:17

import six
from fabric.api import run, settings
# from subprocess import call

__all__ = ('BaseRequirement', 'DebRequirement', 'PyRequirement')


class BaseRequirement(object):

    def __init__(self, requirements=None, install_cmd=None, uninstall_cmd=None, update_cmd=None,
                 install_prompts=None, uninstall_prompts=None, update_prompts=None, **kwargs):
        self._requirements = requirements or []

        self.requirement_handlers = {
            'install': install_cmd,
            'uninstall': uninstall_cmd,
            'update': update_cmd
        }

        self.requirements_prompts = {
            'install': install_prompts or {},
            'uninstall': uninstall_prompts or {},
            'update': update_prompts or {}
        }

    def handle_requirements(self, action, name=None):
        """
        Handle requirement depends on the action
        """
        if action and not isinstance(action, six.string_types):
            raise TypeError('action: {} should be a string type value!'.format(action))

        if action not in self.requirement_handlers:
            raise ValueError('Unknow action: {}!'.format(action))

        if name and not isinstance(name, six.string_types):
            raise ValueError('name should be a string type value!')

        handler = self.requirement_handlers[action]
        requirements = [name] if name else self._requirements
        with settings(prompts=self.requirements_prompts[action]):
            for name in requirements:
                run('{} {}'.format(handler, name))

    def install_requirements(self, name=None):
        """
        Install the specified requirement with name or install all requirement
        """
        self.handle_requirements('install', name)

    def update_requirements(self, name=None):
        self.handle_requirements('update', name)

    def uninstall_requirements(self, name=None):
        self.handle_requirements('uninstall', name)


class DebRequirement(BaseRequirement):
    """
    Requirement tools to install/unistall package in debian-based OS system
    """

    def __init__(self, requirements=None, **kwargs):
        kwargs['uninstall_prompts'] = {'Do you want to continue? [Y/n] ': 'Y'}
        super(DebRequirement, self).__init__(requirements=requirements,
                                             install_cmd='sudo apt-get install',
                                             uninstall_cmd='sudo apt-get remove',
                                             **kwargs)


class PyRequirement(BaseRequirement):
    """
    Requirement tools to install/uninstall/update package for python
    """

    def __init__(self, requirements=None, version=2, **kwargs):
        kwargs['uninstall_prompts'] = {'Proceed (y/n)? ': 'y'}
        if version == 3:
            super(PyRequirement, self).__init__(requirements=requirements,
                                                install_cmd='sudo -H pip3 install ',
                                                uninstall_cmd='sudo -H pip3 uninstall ',
                                                update_cmd='sudo -H pip3 install -U ', **kwargs)
        else:
            super(PyRequirement, self).__init__(requirements=requirements,
                                                install_cmd='sudo -H pip install ',
                                                uninstall_cmd='sudo -H pip uninstall ',
                                                update_cmd='sudo -H pip install -U ', **kwargs)

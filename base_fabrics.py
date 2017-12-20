# -*- coding: utf-8 -*-
# @Author: theo-l
<<<<<<< HEAD
# @Date:   2017-09-08 11:52:55
# @Last Modified by:   theo-l
# @Last Modified time: 2017-09-12 15:53:48
import six
from fabric.api import run, settings
DEBUG = True


class HostConfig:

    def __init__(self, host_config=None, *args, **kwargs):
        """
        host_config: a list of tuple about the host information (host_string, password, host_name, host_role)
        """

        self._config = host_config or []
        self.all_host_strings = set()

        self.all_host_names = set()
        self.all_host_roles = set()
        self.host_string_password_map = {}
        self.host_string_name_map = {}
        self.host_string_role_map = {}

        for host in self._config:
            self.all_host_strings.add(host[0])
            self.all_host_names.add(host[2])
            self.all_host_roles.add(host[3])
            self.host_string_password_map[host[0]] = host[1]
            self.host_string_name_map[host[0]] = host[2]
            self.host_string_role_map[host[0]] = host[3]

        if DEBUG:
            print(self.all_host_names)
            print(self.all_host_strings)
            print(self.all_host_roles)
            print(self.host_string_password_map)
            print(self.host_string_name_map)
            print(self.host_string_role_map)

        self.name_host_strings_map = self._build_role_or_name_host_string_map(reverse_data=self.host_string_name_map)
        self.role_host_string_map = self._build_role_or_name_host_string_map(reverse_data=self.host_string_role_map)

        if DEBUG:
            print(self.name_host_strings_map)
            print(self.role_host_string_map)

        setattr(self, 'ALL_HOSTS', self.all_host_strings)
        for name in self.all_host_names:
            setattr(self, '{}_HOSTS'.format(name.upper()), self.name_host_strings_map[name])

        setattr(self, 'ALL_ROLES', self.all_host_strings)
        for role in self.all_host_roles:
            setattr(self, '{}_ROLES'.format(role.upper()), self.role_host_string_map[role])

    def setup_fabric_env(self, env):
        """
        Use the attribute value to init fabric's env instance, including:
            1. hosts
            2. passwords
            3. roles
        """
        env.hosts = self.all_host_strings
        env.passwords = self.host_string_password_map
        env.roledefs.update(self.role_host_string_map)

    @staticmethod
    def _build_role_or_name_host_string_map(reverse_data=None):
        """
        Build a map data structure: name/role to a list of host strings:

        Example:
            TEST:[host1, host2, host3,...]
            PROD:[host1, host2, host3,...]
        """
        if reverse_data is None:
            return {}

        data = {}
        for host_string, role_or_name in reverse_data.iteritems():
            data.setdefault(role_or_name, [])
            data[role_or_name].append(host_string)
        return data


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
=======
# @Date:   2017-06-26 18:52:29
# @Last Modified by:   theo-l
# @Last Modified time: 2017-06-26 18:52:34
# 
>>>>>>> a1c36b07fbdd3d2c91462ecec37ffa8a83176473

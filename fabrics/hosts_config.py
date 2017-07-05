# -*- coding: utf-8 -*-
# @Author: theo-l
# @Date:   2017-07-01 16:47:16
# @Last Modified by:   theo-l
# @Last Modified time: 2017-07-05 11:58:31


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

        print(self.all_host_names)
        print(self.all_host_strings)
        print(self.all_host_roles)
        print(self.host_string_password_map)
        print(self.host_string_name_map)
        print(self.host_string_role_map)

        self.name_host_strings_map = self._build_role_or_name_host_string_map(reverse_data=self.host_string_name_map)
        self.role_host_string_map = self._build_role_or_name_host_string_map(reverse_data=self.host_string_role_map)

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

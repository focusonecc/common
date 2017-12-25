# -*- coding: utf-8 -*-
# @Author: theo-l
# @Date:   2017-07-01 16:47:16
# @Last Modified by:   theo-l
# @Last Modified time: 2017-07-05 11:58:31


class HostConfig:
    """
    Usage:

    # 定义相关主机数据信息， 可以定义多个主机
    HOST_CONFIG = [
            # (主机地址， 主机密码， 主机名称<可重复>， 主机角色<可重复>)  当可重复字段重复时对应多个主机
            ('vagrant@192.168.33.10:22', 'vagrant', 'dev', 'dev')
    ]

    # 初始化主机配置管理实例对象
    host_config  = HostConfig(host_config=HOST_CONFIG)
    # 利用主机配置管理实例对象来配置Fabric的全局实例
    host_config.setup_fabric_env(env)


    # 根据主机名称来指定主机列表来定义task
    @task
    @hosts(host_config.DEV_HOSTS) # 注意这里的 DEV 对应 HOST_CONFIG 中定义的主机的名称字段 dev 的大写
    def task_name():
        ....
        pass

    # 根据角色名称来指定主机列表来定义task
    @task
    @roles(host_config.DEV_ROLES) # 注意这里的 DEV 对应 HOST_CONFIG 中定义的主机的角色字段 dev 的大写
    def task_name():
        ...
        pass

    """

    def __init__(self, host_config=None, *args, **kwargs):
        """
        host_config: 关于主机信息的一个元组数据列表, 其形式如下
            (host_string, password, host_name, host_role)
           例如:
            ('vagrant@192.168.33.10:22', 'vagrant', 'dev', 'dev')
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

        self.name_host_strings_map = self._build_role_or_name_host_string_map(reverse_data=self.host_string_name_map)
        self.role_host_string_map = self._build_role_or_name_host_string_map(reverse_data=self.host_string_role_map)


        setattr(self, 'ALL_HOSTS', self.all_host_strings)
        for name in self.all_host_names:
            setattr(self, '{}_HOSTS'.format(name.upper()), self.name_host_strings_map[name])

        setattr(self, 'ALL_ROLES', self.all_host_strings)
        for role in self.all_host_roles:
            setattr(self, '{}_ROLES'.format(role.upper()), self.role_host_string_map[role])

    def setup_fabric_env(self, env):
        """
        将解析过后的主机初始化数据写入到fabric的全局变量 env 中方便后续操作,主要包括:
            1. 主机 hosts
            2. 主机密码数据: passwords
            3. 主机的角色数据: roledefs
        """
        env.hosts = self.all_host_strings
        env.passwords = self.host_string_password_map
        env.roledefs.update(self.role_host_string_map)

    @staticmethod
    def _build_role_or_name_host_string_map(reverse_data=None):
        """
        Build a map data structure: name/role to a list of host strings:

        构建一个主机名称/主机角色名称 => 到主机地址字符串列表的映射

        例如
            主机名称: [主机地址1， 主机地址2， 主机地址3，...]
            角色名称: [主机地址1， 主机地址2， 主机地址3，...]

        """
        if reverse_data is None:
            return {}

        data = {}
        for host_string, role_or_name in reverse_data.items():
            data.setdefault(role_or_name, [])
            data[role_or_name].append(host_string)
        return data





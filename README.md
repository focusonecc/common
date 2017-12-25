#  Django 后端开发的通用应用组件 Common 


Create this repository to maintain the most used common functions in a module, for convinient reason

This module include the following common function features:
1. Customized Django-related utils
2. Customized Tastypie-related utils
3. Customized Testing-related utils
4. Project scope constants
5. Project scope model choices
6. Customized Fabric-related utils


dependencies
- Django 
- tastypie
- Fabric / requries
- factory
- faker

## 在Django后端项目的开发和部署中使用该repo的说明

1. 在Django的开发项目中使用该repo的说明
    
        # 1. 进入到Django开发项目目录中，将该repo添加为项目的submodule， 会自动clone该repo
        git submodule add https://github.com/focusonecc/common
        
        # 2. 在开发过程中更新该commonrepo的方法
        git submodule foreach git pull origin master
   
2. 在服务器端部署Django项目时同步该repo的说明

        #在Django项目中运行以下的git命令:
        git submodule foreach git pull origin master


### Fabric usage case ###
```python
"""
A demo for the fabrics tool
"""

from fabric.api import (env, task, hosts)
from fabrics import HostConfig, DebRequirement, PyRequirement

# Remote host general configurations
HOST_CONFIG = [
    ('vagrant@192.168.33.10:22', 'vagrant', 'dev', 'dev') #hostring, password, name, role
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
```

Then in terminal, we can run the following commands:
```sh
fab setup_all # init the environment for all hosts
fab reset_all # clean the environment for all hosts
```

### django field's choices base usage demo ###

```python
from common.base_choices import (ChoiceItem, BaseChoice)

class HttpMethodChoice(BaseChoice):
    """
    General API request method choices
    """
    GET = ChoiceItem(1, 'HTTP GET')
    POST = ChoiceItem(2, 'HTTP POST')
    PUT = ChoiceItem(3, 'HTTP PUT')
    PATCH = ChoiceItem(4, 'HTTP PATCH')
    DELETE = ChoiceItem(5, 'HTTP DELETE')


############################################################
# In django model definitions
############################################################
from django.db  import models
from common.models import BaseModel

class APIInfo(BaseModel):

    method = models.IntegerField(verbose_name='Request Method', choices=HttpMethodChoice.choices, default=HttpMethodChoice.GET)
    ...

```

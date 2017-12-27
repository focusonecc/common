#  Django 后端开发的通用应用组件(Common)


## 项目简介
创建这个repo主要是为了统一集中来维护在我们的后端开发过程中会经常使用到的一些功能模块， 使得代码本身的质量和文档更加完善和规范，提高项目开发过程效率。 

当前这个repo拟定包含以下的通用功能模块:

- Django相关的常用工具模块 django
- Tastypie相关的常用工具模块 tastypie
- Testing相关的常用工具模块 tests
- Fabric相关的常用工具模块 fabrics 
- 推送相关的常用工具模块 notification
- 地理位置服务工具模块 geo 
- 服务器部署相关的标准配置文件模板 config 
- 支付相关的常用工具模块 payment
- 其他一些常用功能模块(例如日期转换， url操作等) utils

**注意说明， 在项目开发过程中，尽量不要在项目中直接修改该模块， 有任何修改请在该repo中维护后再更新到项目中， 这样能够保证该repo在所有项目中的完整性**

## 项目依赖
- Django 
- tastypie
- Fabric 
- factory
- faker

## 项目使用说明

1. 在Django的开发项目中使用该repo的说明
    
        # 1. 进入到Django开发项目目录中，将该repo添加为项目的submodule， 会自动clone该repo
        git submodule add https://github.com/focusonecc/common
        
        # 2. 在开发过程中更新该commonrepo的方法
        git submodule foreach git pull origin master
   
2. 在服务器端部署Django项目时同步该repo的说明

        #在Django项目中运行以下的git命令:
        git submodule foreach git pull origin master


## 相关模块的使用案例
### 1. Fabric 主机管理器使用案例

1. 在项目的根目录下定义fabfile.py， 内容如下:

        from fabric.api import (env, task, hosts, roles)
        from common.fabrics.import HostConfig 
        
        # Remote host general configurations
        HOST_CONFIG = [
            ('vagrant@192.168.33.10:22', 'vagrant', 'dev', 'dev'), #hostring, password, name, role
        ]
        
        host_config = HostConfig(host_config=HOST_CONFIG)
        host_config.setup_fabric_env(env)
        
        
        @task
        @hosts(host_config.DEV_HOSTS) # 注意此处的 DEV 对应 HOST_CONFIG 中的 dev 主机名
        def taskname1():
            #...
            pass
        
        @task
        @roles(host_config.DEV_ROLES) # 注意此处的 DEV 对应 HOST_CONFIG 中的 dev 角色名 
        def taskname2():
            # ...
            pass

2. 然后在终端中就可以按照以下方式来调用上述定义的task

        fab taskname1
        fab taskname1

### 2. Django  model 字段的choice选项类用例

1. 定义一个选项Choice类

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

2. 在model中定义字段时使用

        from django.db  import models
        from common.models import BaseModel
        
        class APIInfo(BaseModel):
        
            method = models.IntegerField(verbose_name='Request Method', choices=HttpMethodChoice.choices, 
                                         default=HttpMethodChoice.GET)
            ...

# -*- coding: utf-8 -*-
# @Author: theo-l
# @Date:   2017-09-11 10:39:29
# @Last Modified by:   theo-l
# @Last Modified time: 2017-09-15 17:41:09

import six
from django.conf.urls import url
from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import Paginator
from django.db.models.query import QuerySet, Q
from django.db import models
from django.http import Http404, JsonResponse
from django.views.generic import ListView
from django.views.generic.edit import ModelFormMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _
from django.urls import reverse


class XView(ListView, ModelFormMixin):
    ###########################################################
    # attribute access method
    ###########################################################

    # FormMixin
    initial = {}
    form_class = None  # 指定model详情页面form类
    pk_url_kwargs = 'pk'  # 指定model详情页面url对应的kwargs名称

    resource_name = None  # 定义URLconf中的resource部分的名称, 默认为model名称

    # attributes of MultipleObjectMixin
    allow_empty = True
    queryset = None
    model = None
    ordering = None  # 指定那些字段可以被用来在model列表页面进行排序
    page_kwargs = 'page'
    paginate_by = None
    paginate_orphans = 0
    paginator_class = Paginator
    context_object_list_name = None # model 列表页面的数据列表实例对象
    request_order_key_name = 'order_by'

    fields = None  # specify which fields should be display on the detail page's factory form

    list_template_name = None  # 指定model列表页面的模板文件名称
    detail_template_name = None  # 指定model详情页面的模板文件名称
    list_template_suffix = '_list'  # 指定model列表页面的模板文件名后缀
    detail_template_suffix = '_detail'  # 指定model详情页面的模板文件名后缀

    context_object_name = None # 指定model详情页面中的上下文实例对象名称
    context_form_object_name = 'form'
    search_key_name = 'qk'  # 默认搜索关键字名称 the keyword search name
    search_key_type = 'qt' # 默认的关键字搜索类型 **Deprecated**
    search_fields = []  # 可以被用来进行搜索的model的字段名称列表
    detail_add_url_suffix = 'detail' # model的默认编辑页面url的后缀

    app_label = None  # 当前视图所在的Django应用名称， 主要用来反向解析URL

    # 用来构建默认的列表/详情的URL的名称后缀
    list_url_name_suffix = '_manager'  # url(regex, view, name='resource_name'+'_manager')
    detail_url_name_suffix = '_detail'  # url(regex, view, name='resource_name'+'_detail')

    detail_form_action_url_name = 'form_action'  # 一个模板上线文变量用来在model详情页面的表单的action使用的URL上
    new_detail_url_name = 'new_detail_url'  # 一个模板上下文变量用来访问model创建页面的url
    list_url_name = 'list_url'  #  一个模板上下文变量用来访问model的列表页面的url


    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        """
        根据用户请求方式以及页面类型来将请求转发到相应的视图中
        """
        method_name = request.method.lower()
        self.request_type = 'list' if kwargs.get(self.pk_url_kwargs, None) is None else 'detail'

        if method_name in self.http_method_names:
            handler = getattr(self, '{}_{}'.format(method_name, self.request_type), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)


    @property
    def urls(self):
        urls = [
            url(r'{}/$'.format(self.get_resource_name()), self.__class__.as_view(),
                name=self.get_list_url_name()),
            url(r'{}/(?P<{}>[\w\d-]+)/$'.format(self.get_resource_name(), self.pk_url_kwargs), self.__class__.as_view(),
                name=self.get_detail_url_name()),
        ]

        return self.prepend_urls() + urls


    def prepend_urls(self):
        """
        add custom urls to process before the default configuration
        """
        return []


    def get_resource_name(self):
        """
        构造model资源URL的主要部分
        """

        if self.resource_name:
            return self.resource_name
        elif self.model:
            return self.model._meta.model_name
        elif self.queryset:
            return self.queryset.model._meta.model_name
        else:
            raise ImproperlyConfigured(
                    "You need specify at least one of the attributes (resource_name, model, queryset)"
            )


    def get_detail_url_name(self):
        """
        构造model资源详情URLconf的名称
        """
        return '{}{}'.format(self.get_resource_name(), self.detail_url_name_suffix)


    def get_list_url_name(self):
        """
        构造model资源列表URLConf的名称
        """
        return '{}{}'.format(self.get_resource_name(), self.list_url_name_suffix)


    def get_success_url(self):
        """
        重载方法:构造model资源详情页面表单action处理结果的URL
        """
        return reverse(
                '{}:{}'.format(self.app_label,
                               self.get_list_url_name()) if self.app_label else self.get_list_url_name())


    def get_list_url(self):
        """
        构造model资源列表页面的URL
        """
        return reverse(
                '{}:{}'.format(self.app_label,
                               self.get_list_url_name()) if self.app_label else self.get_list_url_name())


    def get_list(self, request, *args, **kwargs):
        """
        model资源的列表数据响应视图
        """

        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, 'exists'):
                is_empty = not self.object_list.exists()
            else:
                is_empty = len(self.object_list) == 0
            if is_empty:
                raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.") % {
                    'class_name': self.__class__.__name__,
                })
        return self.render_to_response(self.get_context_data(**kwargs))


    def get_detail(self, request, *args, **kwargs):
        """
        处理model资源详情请求的默认视图, 根据 get_object 返回的结果:
            1. 如果pk参数对应了一个model实例对象，意味着更新实例
            2. 否则， 意味着新建一个实例
        """

        self.object = self.get_object()
        return self.render_to_response(self.get_context_data(**kwargs))


    def get_object(self, queryset=None):
        """
        用来初始化model详情页面请求， 同时检查相应model实例对象
        """
        queryset = queryset or self.get_queryset()
        try:
            pk = self.kwargs.get(self.pk_url_kwargs)
            return queryset.filter(pk=pk).get()
        except Exception:
            return None


    def post_list(self, request, *args, **kwargs):
        """
        用来处理创建一个新对象的请求视图
        """
        print('POST List: {}'.format(request.path_info))
        form = self.get_form()
        if form.is_valid():
            print('valid post')
            return self.form_valid(form)
        else:
            print('invalid post')

            return self.form_invalid(form)


    def post_detail(self, request, *args, **kwargs):
        """
        用来更新一个model实例对象的请求视图
        """
        print('POST Detail: {}'.format(request.path_info))

        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            print(form.errors)
            return self.form_invalid(form)


    def get_detail_context_data(self, **kwargs):
        """
        构造model详情页面的上下文变量
        """

        context = {}
        if self.context_form_object_name not in kwargs:
            kwargs[self.context_form_object_name] = self.get_form()

        if self.detail_form_action_url_name not in kwargs:
            kwargs[self.detail_form_action_url_name] = self.get_detail_form_action_url()

        context.update(kwargs)
        if hasattr(self, 'object') and self.object is not None:
            context['object'] = self.object
            context_object_name = self.get_detail_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object

        # Insert the detail template names to context
        context.update({'template': self.get_detail_template_names()})

        self._show_context_data(context)
        return context


    def get_detail_form_action_url(self):
        """
        构造model详情页面的表单action的提交的URL
        """
        if hasattr(self, 'object') and self.object:
            return reverse('{}:{}'.format(self.app_label,
                                          self.get_detail_url_name()) if self.app_label else self.get_detail_url_name(),
                           kwargs={self.pk_url_kwarg: self.object.pk})
        return reverse(
                '{}:{}'.format(self.app_label,
                               self.get_list_url_name() if self.app_label else self.get_list_url_name()))


    def get_list_context_data(self, **kwargs):
        """
        构造model列表页面模板的上下文变量集合
        """
        context = {}
        context.update(kwargs)

        context.update({'template': self.get_list_template_names()})
        queryset = kwargs.pop('object_list', self.object_list)
        page_size = self.get_paginate_by(queryset)
        context_object_name = self.get_list_content_object_name(queryset)
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
            context.update({

                'paginator'   : paginator,
                'page_obj'    : page,
                'is_paginated': is_paginated,
                'object_list' : queryset
            })
            if context_object_name is not None:
                context[context_object_name] = self.reorder_context_queryset(queryset)
        else:
            context.update({

                'paginator'   : None,
                'page_obj'    : None,
                'is_paginated': None,
                'object_list' : queryset
            })
            if context_object_name is not None:
                context[context_object_name] = self.reorder_context_queryset(queryset)

        context[self.new_detail_url_name] = ''.join([reverse(
                '{}:{}'.format(self.app_label,
                               self.get_list_url_name()) if self.app_label else self.get_list_url_name()),
            self.detail_add_url_suffix, '/'])
        self._show_context_data(context)
        return context


    def _show_context_data(self, context):
        print('get {} context:'.format(self.request_type))
        for key, value in context.items():
            value = value.encode('utf-8') if isinstance(value, six.string_types) else value
            print('  {} => {}'.format(key, value))


    def get_context_data(self, **kwargs):
        """
        顶层的模板上下文数据准备方法
        """
        context = {}
        context['view'] = self
        # Insert the url kwargs to context data
        context.update(**kwargs)
        # Insert the request GET query data into context
        context.update(**{key: value.strip() for key, value in self.request.GET.dict().items()})
        context[self.list_url_name] = self.get_list_url()

        # Insert the detail/list context data to context
        extra_context_method = getattr(self, 'get_{}_context_data'.format(self.request_type), None)
        if extra_context_method is not None:
            return extra_context_method(**context)
        return context


    def remove_url_keys(self, kwargs):
        """
        将以下的参数从请求的查询参数中去除:
            1. paginator params
            2. keyword search  name
            3. keyword search type
            4. request order by key name
        """
        for key in [self.page_kwarg, self.search_key_name, self.search_key_type, self.request_order_key_name]:
            if key in kwargs:
                del kwargs[key]


    def get_queryset(self):
        """
        重载方法用来实现列表页面数据的更加复杂的操作， 包括:
            1. 关键字检索
            2. 客户端动态排序请求
            3. model字段过滤
        """
        queryset = super(XView, self).get_queryset()
        queries = self.request.GET.copy()

        request_order = self.get_order_by_query(queries)

        # keyword search
        keyword = queries.get(self.search_key_name, '').strip()
        if keyword:
            q = Q()
            for field in self.search_fields:
                q = Q(**{'{}__icontains'.format(field): keyword}) | q
            queryset = queryset.filter(q)

        self.remove_url_keys(queries)
        filters = self.build_filters(**queries)

        # model fields' filter
        if filters:
            queryset = queryset.filter(**filters)

        # request ordering sort
        if request_order:
            queryset = queryset.order_by(*request_order)

        return queryset


    def render_to_response(self, context, **response_kwargs):
        """
        重载方法， 用来使用定制的模板来渲染响应的结果
        """
        response_kwargs.setdefault('content_type', self.content_type)
        self._show_context_data(response_kwargs)
        return self.response_class(request=self.request, template=context['template'],
                                   context=context, using=self.template_engine, **response_kwargs)


    def json_response(self, data):
        """
        为客户端请求返回一个接送数据对象
        """
        return JsonResponse(data)


    def get_detail_template_names(self):
        """
        返回详情页面模板文件名称
        """

        if self.detail_template_name is not None:
            return [self.detail_template_name]

        names = []
        if hasattr(self, 'object') and self.object is not None and isinstance(self.object, models.Model):
            meta = self.object._meta
        elif hasattr(self, 'model') and self.model is not None and issubclass(self.model, models.Model):
            meta = self.model._meta
        elif hasattr(self, 'queryset') and self.queryset is not None and isinstance(self.queryset, QuerySet):
            meta = self.queryset.model._meta

        if meta is not None:
            names.append('{}/{}{}.html'.format(meta.app_label, meta.model_name, self.detail_template_suffix))

        if not names:
            raise ImproperlyConfigured(
                    "XView requires either a definition of "
                    "'detail_template_name' or an model attribute")
        return names


    def get_list_template_names(self):
        """
        返回列表页面模板文件名称
        """

        if self.list_template_name is not None:
            return [self.list_template_name]
        names = []
        if hasattr(self, 'object_list') and self.object_list is not None and isinstance(self.object_list, QuerySet):
            meta = self.object_list.model._meta
        elif hasattr(self, 'model') and self.model is not None and issubclass(self.model, models.Model):
            meta = self.model._meta
        elif hasattr(self, 'queryset') and self.queryset is not None and isinstance(self.queryset, QuerySet):
            meta = self.queryset.model._meta
        else:
            meta = None

        if meta is not None:
            names.append('{}/{}{}.html'.format(meta.app_label, meta.model_name, self.list_template_suffix))

        if not names:
            raise ImproperlyConfigured(
                    "XView requires either a definition of "
                    "'list_template_name' or an model attribute")

        return names


    def get_detail_context_object_name(self, obj):
        """
        返回详细上下文中的model实例对象名称
        """
        if self.context_object_name:
            return self.context_object_name
        elif isinstance(obj, models.Model):
            return obj._meta.model_name
        else:
            return None


    def get_list_content_object_name(self, object_list):
        """
        返回列表上下文中的model实例对象名称
        """
        if self.context_object_list_name:
            return self.context_object_list_name
        if hasattr(object_list, 'model'):
            return '{}_list'.format(object_list.model._meta.model_name)
        else:
            return None


    def build_filters(self, **filters):
        """
        在此可以用来定制更多的过滤动作条件
        """
        return {k: v for k, v in filters.items() if v}


    def get_order_by_query(self, queries):
        """
        accept order by params from the client request url to sort the list data
        ordering params can specify default list data sort
        """
        if self.request_order_key_name in queries:
            return [f for f in queries.getlist(self.request_order_key_name) if f]
        return []


    def reorder_context_queryset(self, queryset):
        """
        一个用来给列表请求的最终的数据列表进行排序的接口
        """
        return queryset

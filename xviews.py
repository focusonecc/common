# -*- coding: utf-8 -*-
# @Author: theo-l
# @Date:   2017-09-11 10:39:29
# @Last Modified by:   theo-l
# @Last Modified time: 2017-09-15 17:41:09

# -*- coding: utf-8 -*-
# @Author: theo-l
# @Date:   2017-08-01 07:55:46
# @Last Modified by:   theo-l
# @Last Modified time: 2017-08-09 20:45:54

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
    form_class = None
    pk_url_kwargs = 'pk'

    resource_name = None  # define the  URLconf's resource name

    # attributes of MultipleObjectMixin ####
    allow_empty = True
    queryset = None
    model = None
    ordering = None  # specify which fields should be used to sort the data in list page
    page_kwargs = 'page'
    paginate_by = None
    paginate_orphans = 0
    paginator_class = Paginator
    context_object_list_name = None
    request_order_key_name = 'order_by'

    form_class = None  # specify which form be used in the detail page
    fields = None  # specify which fields should be display on the detail page's factory form

    list_template_name = None
    detail_template_name = None
    list_template_suffix = '_list'
    detail_template_suffix = '_detail'

    context_object_name = None
    context_form_object_name = 'form'
    search_key_name = 'qk'  # the keyword search name
    search_key_type = 'qt'
    search_fields = []  # the field which can be search by keywords
    detail_add_url_suffix = 'detail'

    app_label = None  # current app label which the view belongs to, used to resolve the url

    # used to build the default list&detail url's name suffix
    list_url_name_suffix = '_manager'  # url(regex, view, name='resource_name'+'_manager')
    detail_url_name_suffix = '_detail'  # url(regex, view, name='resource_name'+'_detail')

    detail_form_action_url_name = 'form_action'  # define the context variable name which used to access the form submit action url
    new_detail_url_name = 'new_detail_url'  # define the context variable name which used to access create url
    list_url_name = 'list_url'  # define the context variable name which used to access the list url

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
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
            url(r'{}/$'.format(self.get_resource_name(), self.pk_url_kwargs), self.__class__.as_view(), name=self.get_list_url_name()),
            url(r'{}/(?P<{}>[\w\d-]+)/$'.format(self.get_resource_name(), self.pk_url_kwargs), self.__class__.as_view(), name=self.get_detail_url_name()),
        ]

        return self.prepend_urls() + urls

    def prepend_urls(self):
        """
        add custom urls to process before the default configuration
        """
        return []

    def get_resource_name(self):
        """
        Build the model resource's main part of URL
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
        Build model resource's detail URLConf's name
        """
        return '{}{}'.format(self.get_resource_name(), self.detail_url_name_suffix)

    def get_list_url_name(self):
        """
        Build model resource's list URLConf's name
        """
        return '{}{}'.format(self.get_resource_name(), self.list_url_name_suffix)

    def get_success_url(self):
        """
        Build the url for the detail page's form action url
        """
        return reverse('{}:{}'.format(self.app_label, self.get_list_url_name()) if self.app_label else self.get_list_url_name())

    def get_list_url(self):
        """
        Build the url for the model resource's list page url
        """
        return reverse('{}:{}'.format(self.app_label, self.get_list_url_name()) if self.app_label else self.get_list_url_name())

    def get_list(self, request, *args, **kwargs):
        """
        Model resource's list data view
        """

        print "GET List: {}".format(request.path_info)
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
        Default view to process model resource detail request:
            1. if the pk is corresponed to an object, then means update a model
            2. else means to create a model object
        depends on the get_object method's result

        """

        print "GET Detail: {}".format(request.path_info)
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data(**kwargs))

    def get_object(self, queryset=None):
        """
        Used to init the detail reuqest's model object, check the detail model object at the same time
        """
        queryset = queryset or self.get_queryset()
        try:
            pk = self.kwargs.get(self.pk_url_kwargs)
            return queryset.filter(pk=pk).get()
        except Exception:
            return None

    def post_list(self, request, *args, **kwargs):
        """
        Request to create a new object
        """
        print 'POST List: {}'.format(request.path_info)
        form = self.get_form()
        if form.is_valid():
            print('valid post')
            return self.form_valid(form)
        else:
            print('invalid post')
            return self.form_invalid(form)

    def post_detail(self, request, *args, **kwargs):
        """
        Request to update an existed object
        """
        print 'POST Detail: {}'.format(request.path_info)
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            print form.errors
            return self.form_invalid(form)

    def get_detail_context_data(self, **kwargs):
        """
        Build the context variables for the detail page
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
        Build detail page's form's submit action url
        """
        if hasattr(self, 'object') and self.object:
            return reverse('{}:{}'.format(self.app_label, self.get_detail_url_name()) if self.app_label else self.get_detail_url_name(), kwargs={self.pk_url_kwarg: self.object.pk})
        return reverse('{}:{}'.format(self.app_label, self.get_list_url_name() if self.app_label else self.get_list_url_name()))

    def get_list_context_data(self, **kwargs):
        context = {}
        context.update(kwargs)

        context.update({'template': self.get_list_template_names()})
        queryset = kwargs.pop('object_list', self.object_list)
        page_size = self.get_paginate_by(queryset)
        context_object_name = self.get_list_content_object_name(queryset)
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
            context.update({
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
                'object_list': queryset
            })
            if context_object_name is not None:
                context[context_object_name] = self.reorder_context_queryset(queryset)
        else:
            context.update({
                'paginator': None,
                'page_obj': None,
                'is_paginated': None,
                'object_list': queryset
            })
            if context_object_name is not None:
                context[context_object_name] = self.reorder_context_queryset(queryset)

        context[self.new_detail_url_name] = ''.join([reverse('{}:{}'.format(self.app_label, self.get_list_url_name()) if self.app_label else self.get_list_url_name()), self.detail_add_url_suffix, '/'])
        self._show_context_data(context)
        return context

    def _show_context_data(self, context):
        print 'get {} context:'.format(self.request_type)
        for key, value in context.items():
            value = value.encode('utf-8') if isinstance(value, (str, unicode)) else value
            print '  {} => {}'.format(key, value)

    def get_context_data(self, **kwargs):
        """
        The top level method to prepare context data
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
        Remove the following parameters from the request's query dict:
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
        Override to customize more complex operation on list page, including:
            1. keyword search
            2. client side request dynamic sorting
            3. common model fields' filter
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
        Override the use the customized template in context to render the resposne result
        """
        response_kwargs.setdefault('content_type', self.content_type)
        self._show_context_data(response_kwargs)
        return self.response_class(request=self.request, template=context['template'],
                                   context=context, using=self.template_engine, **response_kwargs)

    def json_response(self, data):
        """
        return a json data for the client
        """
        return JsonResponse(data)

    def get_detail_template_names(self):
        """
        Fetch the detail page's template file
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
        Fetch the list page's template file
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
        if self.context_object_name:
            return self.context_object_name
        elif isinstance(obj, models.Model):
            return obj._meta.model_name
        else:
            return None

    def get_list_content_object_name(self, object_list):
        if self.context_object_list_name:
            return self.context_object_list_name
        if hasattr(object_list, 'model'):
            return '{}_list'.format(object_list.model._meta.model_name)
        else:
            return None

    def build_filters(self, **filters):
        """
        We can customize more filter conditions here to do filter action
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
        Used to reorder the list request's final queryset list data
        """
        return queryset

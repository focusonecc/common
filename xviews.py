# -*- coding: utf-8 -*-
# @Author: theo-l
# @Date:   2017-08-01 07:55:46
# @Last Modified by:   theo-l
# @Last Modified time: 2017-08-02 22:17:02
import six

from django.conf.urls import url
from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import InvalidPage, Paginator
from django.db.models.query import QuerySet
from django.db import models
from django.views.generic import ListView
from django.views.generic.edit import ModelFormMixin
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404
from django.utils.translation import ugettext as _
from django.urls import reverse


class XView(ListView, ModelFormMixin):

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        print(args, kwargs)
        method_name = request.method.lower()
        self.request_type = 'list' if kwargs.get(self.pk_url_kwargs, None) is None else 'detail'
        print('{}_{}'.format(method_name, self.request_type))
        if method_name in self.http_method_names:
            handler = getattr(self, '{}_{}'.format(method_name, self.request_type), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    @property
    def urls(self):
        return [
            url(r'^{}/(?P<{}>[\w\d-]+)?/?$'.format(self.get_resource_name(), self.pk_url_kwargs), self.__class__.as_view(), name=self.get_url_name()),
        ]

    def get_resource_name(self):
        if self.resource_name:
            return self.resource_name
        elif self.model:
            return self.model._meta.model_name
        elif self.queryset:
            return self.queryset.model._meta.model_name
        else:
            return None

    def get_url_name(self):
        return self.get_resource_name()+'-manager'

    def get_list(self, request, *args, **kwargs):
        print("Get object list")
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
        context = self.get_context_data(**kwargs)
        print(context)
        return self.render_to_response(context)

    def get_detail(self, request, *args, **kwargs):
        """
        User request to create a new object or update an exist object
        """
        print("Get object detail")

        self.object = self.get_object()
        form = self.get_form()
        context = self.get_context_data(**kwargs)
        context.update({'form': form})
        print(self.object)
        form_action = reverse(self.get_url_name(), kwargs={'pk':self.object.pk}) if self.object else reverse(self.get_url_name())
        context.update({'form_action':form_action})

        print(context)
        return self.render_to_response(context)

    def get_object(self, queryset=None):
        """
        this method is used to check if current request is create or update an object
        if find object:
            update an exist object
        else:
            create a new object
        """
        queryset = queryset or self.get_queryset()
        try:
            pk = self.kwargs.get(self.pk_url_kwargs)
            if pk is None:
                return None
            else:
                if pk in self.new_kwargs:
                    return None
                else:
                    return queryset.filter(pk=pk).get()

        except Exception:
            return None

    def post_list(self, request, *args, **kwargs):
        """
        Request to create a new object
        """
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def post_detail(self, request, *args, **kwargs):
        """
        Request to update an existed object
        """
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_detail_context_data(self, **kwargs):
        context = {}
        if hasattr(self, 'object') and self.object is not None:
            context['object'] = self.object
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object
        context.update({'template': self.get_detail_template_names()})
        context.update(kwargs)
        return context

    def get_list_context_data(self, **kwargs):
        queryset = kwargs.pop('object_list', self.object_list)
        page_size = self.get_paginate_by(queryset)
        context_object_name = self.get_context_object_list_name(queryset)
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
            context = {
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
                'object_list': queryset
            }
            if context_object_name is not None:
                context[context_object_name] = queryset
        else:
            context = {
                'paginator': None,
                'page_obj': None,
                'is_paginated': None,
                'object_list': queryset
            }
            if context_object_name is not None:
                context[context_object_name] = queryset
        context.update({'template': self.get_list_template_names()})
        context.update(kwargs)
        return context

    def get_context_data(self, **kwargs):
        """
        The top level method to prepare context data
        """
        context = {}
        context['view'] = self
        context['url_name'] = self.get_url_name()
        context.update(**kwargs)
        extra_context_method = getattr(self, 'get_{}_context_data'.format(self.request_type), None)
        if extra_context_method is not None:
            context.update(**extra_context_method())
        return context

###########################################################
# attribute access method
###########################################################
    initial = {}
    form_class = None
    new_kwargs = ['new', 'add', 'create']
    pk_url_kwargs = 'pk'
    model = None
    queryset = None
    ordering = None
    page_kwargs = 'page'
    paginate_by = None
    paginate_orphans = 0
    paginator_class = Paginator
    allow_empty = True
    context_object_name = None
    context_object_list_name = None
    list_template_name = None
    detail_template_name = None
    list_template_suffix = '_list'
    detail_template_suffix = '_detail'
    resource_name=None

    def render_to_response(self, context, **response_kwargs):
        """
        Override the use the customized template in context to render the resposne result
        """
        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(request=self.request, template=context['template'],
                                   context=context, using=self.template_engine, **response_kwargs)

    def get_detail_template_names(self):
        if self.detail_template_name is not None:
            return [self.detail_template_name]

        names = []
        if hasattr(self, 'object') and self.object is not None and isinstance(self.object, models.Model):
            print('access template name by object')
            meta = self.object._meta
        elif hasattr(self, 'model') and self.model is not None and issubclass(self.model, models.Model):
            print('access template name by model')
            meta = self.model._meta
        elif hasattr(self, 'queryset') and self.queryset is not None and isinstance(self.queryset, QuerySet):
            print('access template name by queryset')
            meta = self.queryset.model._meta

        names.append('{}/{}{}.html'.format(meta.app_label, meta.model_name, self.detail_template_suffix))
        if not names:
            raise ImproperlyConfigured(
                "XView requires either a definition of "
                "'detail_template_name' or an model attribute")
        return names

    def get_list_template_names(self):
        if self.list_template_name is not None:
            return [self.list_template_name]

        names = []
        if hasattr(self.object_list, 'model'):
            meta = self.object_list.model._meta
            names.append('{}/{}{}.html'.format(meta.app_label, meta.model_name, self.list_template_suffix))

        if not names:
            raise ImproperlyConfigured(
                "XView requires either a definition of "
                "'list_template_name' or an model attribute")

        return names

    def get_context_object_name(self, obj):
        if self.context_object_name:
            return self.context_object_name
        elif isinstance(obj, models.Model):
            return obj._meta.model_name
        else:
            return None

    def get_context_object_list_name(self, object_list):
        if self.context_object_list_name:
            return self.context_object_list_name
        if hasattr(object_list, 'model'):
            return '{}_list'.format(object_list.model._meta.model_name)
        else:
            return None

# -*- coding: utf-8 -*-
# @Author: theo-l
# @Date:   2017-06-26 18:50:43
# @Last Modified by:   theo-l
# @Last Modified time: 2017-06-26 18:50:43

import warnings
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.db.models.fields.files import ImageField, FileField
from django.db.models.fields import DateField, DateTimeField
from django.http import HttpResponse
from tastypie.exceptions import ImmediateHttpResponse, NotFound
from tastypie.http import HttpUnauthorized, HttpCreated, HttpNoContent
from tastypie.resources import ModelResource, Resource
from tastypie.utils import dict_strip_unicode_keys
from common.utils import datetime2timestamp, get_absolute_url_path
from common import errorcode
from common import messagecode
from common.settings import RESPONSE_CODE_NAME, RESPONSE_MSG_NAME


class BaseModelResource(ModelResource):
    """
    Customized ModelResource
    """

    class Meta:
        excludes = []
        object_class = None

    def validate_required(self, request, deserialized_data=None, require_fields=None):
        """
        Validate required parameter for API access:

        :deserialized_data: deserialized_data of user post parameters
        :require_fields: a list of field name that is required for the API access

        Example:
            deserialized_data = self.deserialize(request)
            self.validate_required(request, deserialized_data, require_fields=['message'])
        """
        deserialized_data = deserialized_data or self.deserialize(request)
        require_fields = require_fields or []
        for field in require_fields:
            if field not in deserialized_data:
                return self.message_response(request, messagecode.PARAM_REQUIRED,
                                             reason='{} is required!'.format(field))
        return True

    def message_response(self, request, code, reason=None):
        """
        Return a response immediately with the given status code and description

        :status_code: ErrorCode instance
        :reason: error description
        :data: extra data returned in the response content

        Example:
            if request.user == obj.creator:
                return self._error_response(request, errorcode.NOT_ALLOWED, reason="Only creator can do action!")
        """
        data = {}
        response_class = HttpUnauthorized if code == messagecode.AUTH_NEEDED else HttpResponse
        data[RESPONSE_CODE_NAME] = code.code
        data[RESPONSE_MSG_NAME] = reason or code.message
        raise ImmediateHttpResponse(
            response=super(BaseModelResource, self).error_response(request, data, response_class))

    def _error_response(self, request, status_code, reason=None, data=None):
        """
        Return a response immediately with the given status code and description

        :status_code: ErrorCode instance
        :reason: error description
        :data: extra data returned in the response content

        Example:
            if request.user == obj.creator:
                return self.error_response(request, errorcode.NOT_ALLOWED, reason="Only creator can do action!")
        """
        warnings.warn('Use message_response instead!')
        data = data or {}
        response_class = HttpUnauthorized if status_code == errorcode.AUTH_NEEDED else HttpResponse
        data['_status'] = status_code
        data['_reason'] = reason or status_code.detail
        raise ImmediateHttpResponse(
            response=super(BaseModelResource, self).error_response(request, data, response_class))

    def build_filters(self, filters=None, ignore_bad_filters=False):
        """
        Make all list API only returned object which enabled=True
        """
        applicable_filters = super(BaseModelResource, self).build_filters(
            filters, ignore_bad_filters)
        if 'pk' not in filters:
            applicable_filters['enabled'] = True
        return applicable_filters

    def deserialize(self, request, data=None, format='application/json'):
        """
        Extract User's request posted data depends on the request content type
        """
        content_type = request.META.get('CONTENT_TYPE', 'application/json')
        if content_type == 'application/x-www-form-urlencoded':  # normal form request
            return request.POST.copy()

        # form request which contains files
        elif content_type.startswith('multipart'):
            data = request.POST.copy()
            if request.FILES:
                data['FILES'] = request.FILES
            return data

        request.META['CONTENT_TYPE'] = 'application/json'
        return super(BaseModelResource, self).deserialize(request, request.body, content_type)

    def dehydrate(self, bundle, exclude_common=True):
        """
        Do some customize behaviors for project requires
            1. convert all DateTimeField's value to a timestamp value
            2. Convert all Media FileField's value to be its absolute url path
            3. if exclude_common = True, the api return value will not includes the common fields
        """
        bundle = super(BaseModelResource, self).dehydrate(bundle)

        for field in bundle.obj._meta.fields:
            # convert all datetime/date to timestamp value

            # used to exclude common model fields
            if exclude_common:
                if field.name in BaseModelResource.Meta.excludes:
                    if field.name in bundle.data:
                        del bundle.data[field.name]
                    continue

            # used to exclude resource specific exclude fields
            if field.name in self._meta.excludes:
                if field.name in bundle.data:
                    del bundle.data[field.name]
                continue

            field_value = getattr(bundle.obj, field.name)
            if not field_value:
                continue
            if isinstance(field, (DateField, DateTimeField)):
                bundle.data[field.name] = datetime2timestamp(field_value)
                continue

            if isinstance(field, (FileField, ImageField)):
                bundle.data[field.name] = get_absolute_url_path(
                    field_value.url)
                continue

        return bundle

    def get_resource_uri(self, bundle_or_obj=None, url_name='api_dispatch_list'):
        """
        Build the resource_uri with absolute host address
        """
        resource_uri = super(BaseModelResource, self).get_resource_uri(
            bundle_or_obj, url_name)

        if resource_uri:
            return '{}{}'.format(settings.HOST.rstrip('/'), resource_uri)

        return resource_uri

    def put_detail(self, request, **kwargs):
        """
        rewrite the parent method to do litter alternatives for the deserialized data
        """
        deserialized = self.deserialize(request)
        deserialized = self.alter_put_detail_deserialized_data(deserialized)

        deserialized = self.alter_deserialized_detail_data(
            request, deserialized)
        bundle = self.build_bundle(
            data=dict_strip_unicode_keys(deserialized), request=request)

        try:
            updated_bundle = self.obj_update(
                bundle=bundle, **self.remove_api_resource_names(kwargs))

            if 'FILES' in deserialized:
                file_keys = [key for key in deserialized['FILES'].keys()]
                obj = updated_bundle.obj
                for key in file_keys:
                    if hasattr(obj, key):
                        setattr(obj, key, deserialized['FILES'][key])
                obj.save()
            self.obj_post_updated(obj)

            if not self._meta.always_return_data:
                return HttpNoContent()
            else:
                # Invalidate prefetched_objects_cache for bundled object
                # because we might have changed a prefetched field
                updated_bundle.obj._prefetched_objects_cache = {}
                updated_bundle = self.full_dehydrate(updated_bundle)
                updated_bundle = self.alter_detail_data_to_serialize(
                    request, updated_bundle)
                return self.create_response(request, updated_bundle)
        except (NotFound, MultipleObjectsReturned):
            updated_bundle = self.obj_create(
                bundle=bundle, **self.remove_api_resource_names(kwargs))
            location = self.get_resource_uri(updated_bundle)

            if not self._meta.always_return_data:
                return HttpCreated(location=location)
            else:
                updated_bundle = self.full_dehydrate(updated_bundle)
                updated_bundle = self.alter_detail_data_to_serialize(
                    request, updated_bundle)
                return self.create_response(request, updated_bundle, response_class=HttpCreated, location=location)

    def obj_post_updated(self, obj):
        """
        一个接口用来调整更新之后的数据对象，某些情形下有用, 可以避免在model中使用
        post_save signal带来的无限递归问题!
        """
        pass

    def alter_put_detail_deserialized_data(self, deserialzed_data):
        """
        一个接口用来调整使用 deserialized 之后得到的数据
        """
        return deserialzed_data


class BaseCommonResource(Resource):
    """
    Customized non-ORM common resource
    """
    pass

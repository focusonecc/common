# -*- coding: utf-8 -*-
# @Author: theo-l
# @Date:   2017-09-08 10:58:39
# @Last Modified by:   theo-l
# @Last Modified time: 2017-09-08 11:49:37

from django.conf import settings
from django.db.models.fields.files import ImageField, FileField
from django.db.models.fields import DateField, DateTimeField
from django.http import HttpResponse
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpUnauthorized
from tastypie.resources import ModelResource, Resource
from utils import datetime2timestamp, get_absolute_url_path
from . import messagecode
from .settings import RESPONSE_CODE_NAME, RESPONSE_MSG_NAME


class BaseModelResource(ModelResource):
    """
    Customized ModelResource
    """

    class Meta:
        excludes = ['created_at', 'updated_at', 'enabled']
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
                return self.message_response(request, messagecode.PARAM_REQUIRED, reason=u'{} is required!'.format(field))
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

    def build_filters(self, filters=None, ignore_bad_filters=False):
        """
        Make all list API only returned object which enabled=True
        """
        applicable_filters = super(BaseModelResource, self).build_filters(filters, ignore_bad_filters)
        if 'pk' not in filters:
            applicable_filters['enabled'] = True

        return applicable_filters

    def deserialize(self, request):
        """
        Extract User's request posted data depends on the request content type
        """
        content_type = request.META.get('CONTENT_TYPE', 'application/json')
        if content_type == 'application/x-www-form-urlencoded':  # normal form request
            return request.POST.copy()

        elif content_type.startswith('multipart'):  # form request which contains files
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
                bundle.data[field.name] = get_absolute_url_path(field_value.url)
                continue

        return bundle

    def get_resource_uri(self, bundle_or_obj=None, url_name='api_dispatch_list'):
        """
        Build the resource_uri with absolute host address
        """
        resource_uri = super(BaseModelResource, self).get_resource_uri(bundle_or_obj, url_name)

        if resource_uri:
            return '{}{}'.format(settings.HOST.rstrip('/'), resource_uri)

        return resource_uri


class BaseCommonResource(Resource):
    """
    Customized non-ORM common resource
    """
    pass

#-*- encoding: utf-8 -*-

from tastypie.constants import ALL_WITH_RELATIONS

from common.resources import BaseModelResource
from common import errorcode
from common.auth.authentications import SpoonhuntDeviceAuthentication
from notification.models import Device
from notification.choices import PlatformType

allowed_platforms = [p[0] for p in PlatformType.choices]


class DeviceResource(BaseModelResource):
    class Meta:
        queryset = Device.objects.all()
        resource_name = 'device'
        allowed_methods = ['post', 'get', 'delete']
        authentication = SpoonhuntDeviceAuthentication()
        filtering = {
            'member': ALL_WITH_RELATIONS
        }

    def post_list(self, request, **kwargs):
        data = self.deserialize(request)
        self.validate_required(request, deserialized_data=data, require_fields=[
                               'token', 'udid', 'platform'])

        token = data.get('token')
        udid = data.get('udid')
        platform = data.get('platform').strip()

        if not platform.isdigit():
            self._error_response(request, errorcode.BAD_PARAMS)

        platform = int(platform)
        if platform not in allowed_platforms:
            self._error_response(request, errorcode.NOT_EXISTS)

        filters = {
            'token':token,
            'udid':udid,
            'platform':platform
        }

        if request.user.is_authenticated():
            filters['member'] = request.user 

        device, _ = Device.objects.get_or_create(**filters)
        kwargs['pk'] = device.pk
        return self.get_detail(request, **kwargs)

    def delete_list(self, request, **kwargs):
        data= self.deserialize(request)
        self.validate_required(request, data, ['token', 'udid', 'platform'])
        platform = data.get('platform')
        if not platform.isdigit():
            self._error_response(request, errorcode.BAD_PARAMS)
        token = data.get('token')
        udid=data.get('udid')

        Device.objects.filter(memer = request.user, token=token, udid=udid, platform=platform).delete()
        return super(DeviceResource, self).delete_list(request, **kwargs) 

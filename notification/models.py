# -*- encoding: utf-8 -*-

# from __future__ import unicode_literals

from django.db import models
from common.models import BaseModel
from notification.settings import USER_MODEL as User
from notification.choices import ServiceType, PlatformType, DeviceStatus
from notification.service import ServiceAgent

# Create your models here.


class Device(BaseModel):
    member = models.ForeignKey(User, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, default='')
    status = models.IntegerField(
        choices=DeviceStatus.choices, default=DeviceStatus.ACTIVE)
    token = models.CharField(max_length=200)
    udid = models.CharField(max_length=200)
    platform = models.IntegerField(
        choices=PlatformType.choices, default=PlatformType.IOS)
    last_login = models.DateTimeField(null=True)
    lang_code = models.CharField(max_length=200, blank=True, null=True)

#     def __unicode__(self):
#         return self.name or u''

    def __unicode__(self):
        return '{} - {}'.format(self.name or '', self.get_platform_display()) 
    
    def __str__(self):
        if self.member is not None:
            return self.member.email
        return '{} - {}'.format(self.name or '', self.get_platform_display())

    class Meta:
        verbose_name = verbose_name_plural = u'Device'


class Notification(BaseModel):
    device = models.ForeignKey(Device)
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_success = models.BooleanField(default=False)

    class Meta:
        verbose_name = verbose_name_plural = u'Notification'

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.__unicode__()

    def device_member(self):
        return self.device.member.email

    device_member.short_description = 'Device User'

    @staticmethod
    def notify(member, title, content):
        #####################################
        # push the message title and content
        # to user's all devices
        #####################################
        devices = Device.enables.filter(member=member).order_by('-created_at')
        for device in devices:
            services = ServiceAgent.get_services_by_platform(device.platform)
            is_success = False
            for service in services:
                is_success = service.push(device, title, content)
                if is_success:
                    break
            Notification.objects.create(
                device=device, title=title, content=content, is_success=is_success)
    
    @staticmethod
    def notify_device(device, title, content):
        """
        push the notification message direct to the specified device
        """
        services = ServiceAgent.get_services_by_platform(device.platform)
        is_success = False
        for service in services:
            is_success = service.push(device, title, content)
            if is_success:
                break
        Notification.objects.create(device=device, title=title, content=content, is_success=is_success)
            

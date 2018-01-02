#-*- encoding: utf-8 -*-

from hashlib import md5
import json
import time
from notification import settings
import requests

from notification.choices import PlatformType, ServiceType

from notification.services.umessage import (
    UmengAndroidListcast, UmengAndroidUnicast,
    UmengIOSListcast, UmengIOSUnicast,
    UmengPushClient, UmengAndroidNotification
)


class BaseService(object):

    # 默认支持的推送服务平台: Android, iOS and web
    allowed_platforms = [PlatformType.ANDROID, PlatformType.IOS, PlatformType.WEB]

    def __init__(self):
        pass

    def push(self, device, title, content):
        if device.platform == PlatformType.IOS:
            return self.ios_push(device.token.split(','), title, content)
        elif device.platform == PlatformType.ANDROID:
            return self.android_push(device.token.split(','), title, content)
        else:
            return self.web_push(device.token.split(','), title, content)

    def ios_push(self, tokens, title, content, **kwargs):
        raise NotImplementedError('you need implemented in subclass')

    def android_push(self, tokens, title, content, **kwargs):
        raise NotImplementedError('you need implemented in subclass')

    def web_push(self, tokens, title, content, **kwargs):
        raise NotImplementedError('you need implemented in subclass')

    def support_platform(self, platform):
        """
        检查推送服务是否支持给定的平台
        """
        return platform in self.allowed_platforms


class UmengService(BaseService):
    """
    友盟推送服务的外部封装接口
    """

    allowed_platforms = [PlatformType.IOS, PlatformType.ANDROID]

    def __init__(self, ios_key=None, ios_secret=None, android_key=None, android_secret=None):
        super(UmengService, self).__init__()
        self.ios_key = ios_key or settings.UMENG_IOS_KEY
        self.ios_secret = ios_secret or settings.UMENG_IOS_SECRET
        self.android_key = android_key or settings.UMENG_ANDROID_KEY
        self.android_secret = android_secret or settings.UMENG_ANDROID_SECRET
        self.pushclient = UmengPushClient()

    def ios_push(self, tokens, title, content, custom=None, **kwargs):

        if len(tokens) == 1:
            notification = UmengIOSUnicast(self.ios_key, self.ios_secret)
        else:
            notification = UmengIOSListcast(self.ios_key, self.ios_secret)

        notification.setDeviceToken(','.join(tokens))
        notification.setBadge(1)
        notification.setAlert({
            'title': title or '',
            'body': content or ''
        })
        if settings.UMENG_TEST_MODE:
            notification.setTestMode()
        result = self.pushclient.send(notification)
        return result.status_code == 200

    def android_push(self, tokens, title, content, custom=None, **kwargs):
        if len(tokens) == 1:
            notification = UmengAndroidUnicast(
                self.android_key, self.android_secret)
        else:
            notification = UmengAndroidListcast(
                self.android_key, self.android_secret)

        notification.setDeviceToken(','.join(tokens))
        notification.setTicker(title or '')
        notification.setTicker(title or '')
        notification.setText(content or '')
        if settings.UMENG_TEST_MODE:
            notification.setTestMode()
        notification.goAppAfterOpen()
        notification.setDisplayType(
            UmengAndroidNotification.DisplayType.notification)

        result = self.pushclient.send(notification)
        return result.status_code == 200


class ServiceAgent(object):
    """
    所有推送服务的外部代理接口
    """

    platform_services = {
        PlatformType.IOS: [UmengService(), ],
        PlatformType.ANDROID: [UmengService(), ],
        PlatformType.WEB: [UmengService(), ]
    }

    named_services = {
        'umeng': UmengService()
    }


    @staticmethod
    def get_services_by_platform(platform=PlatformType.IOS):
        """
        返回指定支持指定平台的一个推送服务列表
        """

        if platform not in ServiceAgent.platform_services:
            raise Warning(
                "Don't have any service support platform: {}".format(platform))

        return ServiceAgent.platform_services.get(platform)

    @staticmethod
    def get_service_by_name(service_name):
        """
        根据指定的推送服务名称来获取推送服务实例
        """
        if service_name not in ServiceAgent.named_services:
            raise Warning("Don't have any servce named: {}".format(service_name))

        return ServiceAgent.named_services.get(service_name)

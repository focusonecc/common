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

    # default allowed ios, android and web
    allowed_platforms = [PlatformType.ANDROID,
                         PlatformType.IOS, PlatformType.WEB]

    def __init__(self):
        pass

    def push(self, device, title, content):
        if device.platform == PlatformType.IOS:
            return self.ios_push(device.token.split(','), title, content)
        elif device.platform == PlatformType.ANDROID:
            return self.android_push(device.token.split(','), title, content)
        else:
            return self.web_push(device.token.split(','), title, content)

    def ios_push(self, tokens, title, content):
        raise NotImplementedError('you need implemented in subclass')

    def android_push(self, tokens, title, content):
        raise NotImplementedError('you need implemented in subclass')

    def web_push(self, tokens, title, content):
        raise NotImplementedError('you need implemented in subclass')

    def support_platform(self, platform):
        #####################################
        # check if the service can serve for the
        # given platform
        #####################################
        return platform in self.allowed_platforms


class UmengService(BaseService):

    allowed_platforms = [PlatformType.IOS, PlatformType.ANDROID]

    def __init__(self, ios_key=None, ios_secret=None, android_key=None, android_secret=None):
        super(UmengService, self).__init__()
        self.ios_key = ios_key or settings.UMENG_IOS_KEY
        self.ios_secret = ios_secret or settings.UMENG_IOS_SECRET
        self.android_key = android_key or settings.UMENG_ANDROID_KEY
        self.android_secret = android_secret or settings.UMENG_ANDROID_SECRET
        self.pushclient = UmengPushClient()

    def ios_push(self, tokens, title, content, custom=None):

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

    def android_push(self, tokens, title, content, custom=None):
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

    platform_services = {
        PlatformType.IOS: [UmengService(), ],
        PlatformType.ANDROID: [UmengService(), ],
        PlatformType.WEB: [UmengService(), ]
    }

    @staticmethod
    def get_services_by_platform(platform=PlatformType.IOS):
        #####################################
        # Return a list of service which support the
        # specified platform
        #####################################

        if platform not in ServiceAgent.platform_services:
            raise Warning(
                "Don't have any service support platform: {}".format(platform))

        return ServiceAgent.platform_services.get(platform)

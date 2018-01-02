#-*- encoding: utf-8 -*-

from django.test import TestCase
from notification.service import ServiceAgent
from notification.choices import PlatformType

# Create your tests here.


class NotificationServiceTestCase(TestCase):

    def test_service_not_support_platform(self):
        UNKNOW_PLATFORM = 123
        self.assertRaisesMessage(Warning, "Don't have any service support platform: {}".format(
            UNKNOW_PLATFORM), ServiceAgent.get_services_by_platform, UNKNOW_PLATFORM)

    def test_service_supported_platform(self):
        for platform in [p[0] for p in PlatformType.choices]:
            services = ServiceAgent.get_services_by_platform(platform)
            self.assertIsNotNone(services)

# -*- encoding: utf-8 -*-
from django.conf.urls import url
from notification.views import test_ios_notification, test_android_notification

urlpatterns = [

    url(r'test/ios/$', test_ios_notification, name='test-ios-notification'),
    url(r'test/android/$', test_android_notification, name='test-android-notification'),

    ]
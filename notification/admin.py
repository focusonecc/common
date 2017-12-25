#-*- encoding: utf-8 -*-

from django.contrib import admin
from notification.models import Device, Notification

# Register your models here.


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('member', 'name', 'platform', 'lang_code', 'token', 'udid')
    search_fields = ('udid', 'token')
    list_filter = ('platform',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('device', 'title', 'content', 'is_success')
    search_fields = ('title', 'content')

# -*- encoding: utf-8 -*-

import json

from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponse, JsonResponse

from notification.service import ServiceAgent
from notification.choices import PlatformType

notification_required_fields = ['token', 'title', 'content']


@csrf_exempt
@require_POST
def test_ios_notification(request):
    """
    view api used to test ios notification
    """
    try:
        data = json.loads(request.body)
        for field in notification_required_fields:
            if field not in data:
                return HttpResponse('required field: {} not given!\n'.format(field)) 
            
        return notify_by_platform(PlatformType.IOS, data)
                    
    except Exception as e:
        return HttpResponse('Exception: {}'.format(str(e)))
    

@csrf_exempt
@require_POST
def test_android_notification(request):
    """
    view api used to test android notification
    """
    try:
        data = json.loads(request.body)
        for field in notification_required_fields:
            if field not in data:
                return HttpResponse('required field: {} not given!\n'.format(field)) 
        
        return notify_by_platform(PlatformType.ANDROID, data)
    except Exception as e:
        return HttpResponse('Exception: {}'.format(str(e)))


def notify_by_platform(platform, data):
    
    tokens = data['token'].split(',')
    title = data['title']
    content = data['content']
    services = ServiceAgent.get_services_by_platform(platform)
    notify_success = False
    for service in services:
        if platform == PlatformType.IOS:
            notify_success = service.ios_push(tokens, title, content)
        elif platform == PlatformType.ANDROID:
            notify_success = service.android_push(tokens, title, content)
        if notify_success:
            break
    
        
    result = 'Succeed' if notify_success else 'Failed'
    return HttpResponse(result)

            

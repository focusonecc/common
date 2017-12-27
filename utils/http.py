# -*- encoding: utf-8 -*-

def get_client_ip(request):
    """
    用来获取请求用户的IP地址
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR', '')
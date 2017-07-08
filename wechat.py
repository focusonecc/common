# -*- coding: utf-8 -*-
# @Author: liang
# @Date:   2017-07-06 08:06:44
# @Last Modified by:   theo-l
# @Last Modified time: 2017-07-06 09:07:06

from hashlib import sha1
import random
import string
import time

import requests
from django.core.cache import cache


class WechatSignature(object):

    WEIXIN_ACCESS_TOKEN_API = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={appsecret}'
    WEIXIN_ACCESS_TICKET_API = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={token}&type=jsapi'
    ACCESS_TOKEN_CACHE_KEY = 'weixin_access_token_cache'
    API_TICKET_CACHE_KEY = 'weixin_api_ticket_cache'
    DEBUG = False

    def __init__(self, appid=None, appsecret=None):
        self.appid = appid
        self.appsecret = appsecret

    def get_wechat_signature(self, url):
        api_ticket = self.get_wechat_api_ticket()
        timestamp = int(time.time())
        noncestr = self.get_noncestr()
        str_to_crypt = 'jsapi_ticket={}&noncestr={}&timestamp={}&url={}'.format(api_ticket, noncestr, timestamp, url)
        signature = sha1(str_to_crypt).hexdigest()
        wechat_signature = {
            'appId': self.appid,
            'nonceStr': noncestr,
            'timestamp': timestamp,
            'signature': signature
        }
        return wechat_signature

    def get_wechat_api_ticket(self):
        api_ticket = cache.get(self.API_TICKET_CACHE_KEY)
        if not api_ticket:
            access_token = self.get_wechat_access_token()

            api_ticket = requests.get(self.WEIXIN_ACCESS_TICKET_API.format(token=access_token)).json()
            if api_ticket['errcode'] == 0:
                cache.set(self.API_TICKET_CACHE_KEY, api_ticket, timeout=api_ticket['expires_in'] - 100)
        return api_ticket['ticket']

    def get_wechat_access_token(self):
        access_token = cache.get(self.ACCESS_TOKEN_CACHE_KEY)
        if not access_token:
            access_token = requests.get(self.WEIXIN_ACCESS_TOKEN_API.format(appid=self.appid, appsecret=self.appsecret))
            if 'access_token' in access_token:  # no errcode if Ok
                cache.set(self.ACCESS_TOKEN_CACHE_KEY, access_token, timeout=access_token['expires_in'] - 100)
        return access_token['access_token']

    @staticmethod
    def get_noncestr(length=16):
        return ''.join([random.choice(string.digits + string.ascii_letters) for i in length])

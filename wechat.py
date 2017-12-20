# -*- coding: utf-8 -*-
<<<<<<< HEAD
# @Author: theo-l
# @Date:   2017-09-08 12:12:04
# @Last Modified by:   theo-l
# @Last Modified time: 2017-09-11 21:35:57

import xmltodict
import hashlib
import requests
import time
from six.moves.urllib.parse import quote
from django.core.cache import cache
from django.conf import settings
from collections import OrderedDict
from common.utils import gen_random_str

wechat_base_config = {
    'appId': settings.WECHAT_PAYMENT_APP_ID,
    'appSecret': settings.WECHAT_PAYMENT_APP_SECRET,
    'mchId': settings.WECHAT_PAYMENT_MCH_ID,
    'payApiKey': settings.WECHAT_PAYMENT_API_KEY,
    'notifyUrl': '{}{}'.format(settings.WEBSITE_HOST, "/wechat/notify/")
}


class WechatError(Exception):
    pass


class BaseWechat(object):

    def __init__(self, config=None):
        """
        * 服务号的AppID
        * 服务器号的AppSecret
        * 微信支付商户号
        * 微信支付API密钥（Key）
        * 服务号的OAuth2.0网页授权回调域名（网页授权域名）
        * 公众号支付目录（JSAPI授权目录）
        """
        config = config or wechat_base_config
        self.app_id = config['appId']
        self.app_secret = config['appSecret']
        self.mch_id = config['mchId']
        self.pay_api_key = config['payApiKey']
        self.notify_url = config['notifyUrl']

    def get_noncestr(length=16):
        """
        generate a random string the the specified length
        """
        return gen_random_str(length)

    @staticmethod
    def cache_get(key):
        return cache.get(key)

    @staticmethod
    def cache_set(key, value, timeout):
        cache.set(key, value, timeout=timeout)

    def gen_signature(self, params=None, sign_method=None):
        if not params:
            raise WechatError('Generate signature error: no data to generate signature!')

        params = {k: v for k, v in params.items() if k != 'sign' and v}
        params = OrderedDict(sorted(params.items(), key=lambda i: i[0]))  # make the value ordered
        encode_str = '&'.join(['{}={}'.format(k, v) for k, v in params])
        sign = sign_method(encode_str)
        return sign.hexdigest().upper()

    def verify_signature(self, params=None, sign_method=None):
        raise NotImplemented('You need to implement this method in each subclass')


class WechatJSAPIAuth(BaseWechat):
    """
    所有需要使用JS-SDK的页面必须先注入配置信息，否则将无法调用
    Refer: https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421141115
    """
    ACCESS_TOKEN_CACHE_KEY = 'weixin_access_token'
    API_TICKET_CACHE_KEY = 'weixin_api_ticket'
    WEIXIN_ACCESS_TOKEN_API = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={appsecret}'
    WEIXIN_ACCESS_TICKET_API = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={token}&type=jsapi'

    def gen_jsapi_auth_signature(self, url):
        """
        Generate signature info for jssdk authentication

        refer: https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421141115
        """
        params = {}
        params['timestamp'] = int(time.time())
        params['noncestr'] = self.get_noncestr()
        params['jsapi_ticket'] = self.get_jsapi_ticket()
        signature = self.gen_signature(params, hashlib.sha1)
        params['signature'] = signature
        return params

    def get_jsapi_ticket(self):
        """
        request wechat jsapi_ticket for wechat jsapi signature
        1. check the cached value
        2. request from wechat server if no cache value and cached the response value
        """
        jsapi_ticket = self.cache_get(self.API_TICKET_CACHE_KEY)
        if jsapi_ticket:
            return jsapi_ticket

        access_token = self.get_access_token()
        response = requests.get(self.WEIXIN_ACCESS_TICKET_API.format({'token': access_token})).json()

        if response['errcode'] != 0:
            raise WechatError('Fetch wechat jsapi_ticket error: {}, {}'.format(response['errcode'], response['errmsg']))

        jsapi_ticket = response['ticket']
        self.cache_set(self.API_TICKET_CACHE_KEY, jsapi_ticket, response['expires_in'] - 100)
        return jsapi_ticket

    def get_access_token(self):
        """
        request wechat access_token for jsapi_signature,
        fetch from cache first and then request wechat service if not found cache
        """
        access_token = self.cache_get(self.ACCESS_TOKEN_CACHE_KEY)
        if access_token:
            return access_token

        response = requests.get(self.WEIXIN_ACCESS_TOKEN_API.format({'appid': self.app_id, 'appsecret': self.app_secret})).json()

        if 'errcode' in response:
            raise WechatError('Fetch wechat access_token error:{}, {}'.format(response['errcode'], response['errmsg']))

        access_token = response['access_token']
        self.cache_set(self.ACCESS_TOKEN_CACHE_KEY, access_token, response['expires_in'] - 100)
        return access_token


class WechatWebAuth(BaseWechat):
    """
    Mainly used to get wechat user's openid or other information
    如果用户在微信客户端中访问第三方网页，公众号可以通过微信网页授权机制，来获取用户基本信息，进而实现业务逻辑。
    网页授权流程分为四步：
        1、引导用户进入授权页面同意授权，获取code
        2、通过code换取网页授权access_token（与基础支持中的access_token不同）
        3、如果需要，开发者可以刷新网页授权access_token，避免过期
        4、通过网页授权access_token和openid获取用户基本信息（支持UnionID机制）
    Refer: https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421140842
    """
    WECHAT_WEB_AUTH_URL = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope={scope}&state={state}#wechat_redirect'
    WECHAT_WEB_AUTH_ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid={appid}&secret={secret}&code={code}&grant_type=authorization_code'
    WECHAT_WEB_AUTH_USERINFO_URL = ' https://api.weixin.qq.com/sns/userinfo?access_token={access_token}&openid={openid}&lang={lang}'
    WECHAT_WEB_AUTH_ACCESS_TOKEN_VALIDATE_URL = 'https://api.weixin.qq.com/sns/auth?access_token={access_token}&openid={openid}'

    def gen_openid_oauth_url(self, redirect_uri, state):
        """
        对于以snsapi_base为scope的网页授权，就静默授权的，用户无感知
        如果用户同意授权，页面将跳转至 redirect_uri/?code=CODE&state=STATE
        Refer: https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421140842
        """
        return self.WECHAT_WEB_AUTH_URL.format(appid=self.app_id, scope='snsapi_base', redirect_uri=quote(redirect_uri), state=state)

    def gen_userinfo_oauth_url(self, redirect_uri, state):
        """
        如果用户从公众号的会话或者自定义菜单进入本公众号的网页授权页，即使是scope为snsapi_userinfo，也是静默授权，用户无感知

        如果用户同意授权，页面将跳转至 redirect_uri/?code=CODE&state=STATE
        """

        return self.WECHAT_WEB_AUTH_URL.format(appid=self.app_id, scope='snsapi_userinfo', redirect_uri=quote(redirect_uri), state=state)

    def get_web_access_token(self, code):
        """
        return value specification:
            access_token    网页授权接口调用凭证,注意：此access_token与基础支持的access_token不同
            expires_in  access_token接口调用凭证超时时间，单位（秒）
            refresh_token   用户刷新access_token
            openid  用户唯一标识，请注意，在未关注公众号时，用户访问公众号的网页，也会产生一个用户和公众号唯一的OpenID
            scope   用户授权的作用域，使用逗号（,）分隔
        """
        response = requests.get(self.WECHAT_WEB_AUTH_ACCESS_TOKEN_URL.format(appid=self.app_id, secret=self.app_secret, code=code)).json()
        if 'errcode' in response:
            raise WechatError('Request Wechat web authentication error: {}, {}'.format(response['errcode'], response['errmsg']))
        return response

    def get_user_info(self, access_token, openid, lang='zh_CN'):
        """
        access_token & openid can be fetched by get_web_access_token()
        Return value(user's information):
            openid  用户的唯一标识
            nickname    用户昵称
            sex 用户的性别，值为1时是男性，值为2时是女性，值为0时是未知
            province    用户个人资料填写的省份
            city    普通用户个人资料填写的城市
            country 国家，如中国为CN
            headimgurl  用户头像，最后一个数值代表正方形头像大小（有0、46、64、96、132数值可选，0代表640*640正方形头像），用户没有头像时该项为空。若用户更换头像，原有头像URL将失效。
            privilege   用户特权信息，json 数组，如微信沃卡用户为（chinaunicom）
            unionid 只有在用户将公众号绑定到微信开放平台帐号后，才会出现该字段。
        """
        response = requests.get(self.WECHAT_WEB_AUTH_USERINFO_URL.format(access_token=access_token, openid=openid, lang=lang)).json()
        if 'errcode' in response and response['errcode'] != 0:
            raise WechatError('Fetch user info failed: {}, {}'.format(response['errcode'], response['errmsg']))
        return response

    def validate_access_token(self, access_token, openid):
        """
        can be used to validate the access_token & openid
        """
        response = requests.get(self.WECHAT_WEB_AUTH_ACCESS_TOKEN_VALIDATE_URL.format(access_token=access_token, openid=openid)).json()

        if response.get('errcode', 0) != 0:
            return False
        return True


class WechatOffcialAccountPay(BaseWechat):
    """
    公众号支付
        开发步骤:
            1. 设置支付目录
            2. 设置授权域名

    """

    PREPAY_API_URL = 'https://api.mch.weixin.qq.com/pay/unifiedorder'

    def gen_wechat_pay_signature(self, wechat_prepay_order_data=None):
        """
        Used to generate wechat pay signature to jssdk to do real pay action
        """
        if wechat_prepay_order_data is None:
            raise WechatError('No wechat prepay order data')

        prepay_data = xmltodict.parse(wechat_prepay_order_data)['xml']
        print prepay_data

        result = {
            'appId': self.app_id,
            'timeStamp': str(int(time.time())),
            'nonceStr': self.get_noncestr(32),
            'package': 'prepay_id=' + prepay_data['prepay_id'],
            'signType': 'MD5'
        }

        result['paySign'] = self.gen_signature(result, sign_method=hashlib.md5)

        return result

    def gen_wechat_prepay_order(self, params=None):
        """
        pass the parameters to generate a prepay order on wechat server side and return the information
        then in our own site use these information to request wechat pay
        """
        PREPAY_API_URL = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
        headers = {'Content-Type': 'application/xml'}
        xml = self._build_unifiedorder(params)
        print xml
        response = requests.post(PREPAY_API_URL, data=xml, headers=headers)
        return response.text

    def _build_wechat_prepay_unifiedorder(self, params=None):
        if not params:
            raise WechatError('Require params to generate prepay unified order!')

        params.update({
            'appid': self.app_id,
            'mch_id': self.mch_id,
            'nonce_str': self.get_noncestr(),
            'trade_type': 'JSAPI',
            'notify_url': self.notify_url,
            'sign_type': 'MD5',
            'key': self.pay_api_key
        })

        params['sign'] = self.gen_signature(params, sign_method=hashlib.md5)
        xml_data = []
        for k, v in params.items():
            if k == 'detail':
                data = '<{key}><![CDATA[{value}]]></{key}>'.format(key=k, value=v)
            else:
                data = '<{key}>{value}</{key}>'.format(key=k, value=v)
            xml_data.append(data)

        xml_data.insert(0, '<xml>')
        xml_data.append('</xml>')
        return ''.join(xml_data)
=======
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
>>>>>>> a1c36b07fbdd3d2c91462ecec37ffa8a83176473

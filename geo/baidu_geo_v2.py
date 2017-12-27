# -*- encoding: utf-8 -*-
import warnings
import requests

__all__ = ('BaiduGeoCoderService',)

class BaiduGeoCoderService(object):
    """
    包装了百度地图WEB服务API的类，可以方便调用百度地图web服务API
    """
    api_url = 'http://api.map.baidu.com/geocoder/v2/'

    def __init__(self, api_ak, null=True):
        if not api_ak:
            warnings.warn('Using Baidu map service need an api ak value')
        self.api_ak = api_ak
        self.null = null

    def address_to_location(self, address):
        """
        根据地址来返回地址的经纬度数据元组: (longitude, latitude)
        """
        if not address:
            return (None, None) if self.null else (0.0, 0.0)

        try:
            response = requests.get(self.api_url, params={
                'address': address,
                'ak'     : self.api_ak,
                'output' : 'json'
            }).json()
            return response['result']['location']['lng'], \
                   response['result']['location']['lat']
        except Exception as e:
            return (None, None) if self.null else (0.0, 0.0)

    def location_to_address(self, longitude, latitude):
        """
        根据指定的经纬度来返回对应的地址字符串
        """
        if longitude is None and latitude is None:
            warnings.warn('Can not use None value to get address value!')
            return None

        try:
            response = requests.get(self.api_url, params={
                'location': ','.join([str(latitude), str(longitude)]),
                'output':'json',
                'pois':1,
                'ak':self.api_ak
            }).json()
            return response
        except Exception as e:
            return None



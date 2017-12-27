# 通用地图服务功能模块

在项目开发的过程中， 我们会用到地址<->经纬度之间的转换或其他相关的功能来实现一些功能。

## 1. 百度地图WEB服务API封装服务
- common.geo.BaiduGeoCoderService
    - address_to_location(address): 实现地址到经纬度的转换
    - location_to_address(longitude, latitude): 实现经纬度到地址的转换

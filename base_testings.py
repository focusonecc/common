# -*- coding: utf-8 -*-
# @Author: theo-l
# @Date:   2017-06-26 18:50:57
# @Last Modified by:   theo-l
# @Last Modified time: 2017-06-26 21:40:34

from tastypie.test import ResourceTestCaseMixin
from django.test import TestCase

from six.moves.urllib_parse import urlparse, urlencode


class APIBaseTestCase(ResourceTestCaseMixin, TestCase):

    api_prefix = '/api/v1/'
    resource_name = None

    def setUp(self):
        """
        Init test case envs
        """
        super(APIBaseTestCase, self).setUp()
        self.more_setup()
        self.setup_endpoints()

    def setup_endpoints(self):
        self.list_endpoint = self.api_prefix + '{}/'.format(self.resource_name)
        self.detail_endpoint = self.api_prefix + '{}/{}/'.format(self.resource_name)

    def get_credentials(self):
        return None

    def post(self, data=None, format='json', endpoint=None, auth=True):
        data = data or {}
        endpoint = endpoint or self.list_endpoint
        authentication = self.get_credentials() if auth else None
        return self.api_client.post(endpoint, format=format, data=data, authentication=authentication)

    def get(self, data=None, format='json', endpoint=None, auth=True):
        endpoint = endpoint or self.list_endpoint
        is_query_endpoint = urlparse(endpoint).query
        authentication = self.get_credentials() if auth else None
        if data:
            query_pattern = '{}&{}' if is_query_endpoint else '{}?{}'
            endpoint = query_pattern.format(endpoint, urlencode(data, True))
        return self.api_client.get(endpoint, format=format, authentication=authentication)

    def post_form(self, data=None, endpoint=None, auth=True):
        data = data or {}
        endpoint = endpoint or self.list_endpoint
        authentication = self.get_credentials() if auth else None
        return self.client.post(endpoint, data=data, HTTP_AUTHORIZATION=authentication)

    def delete(self, data=None, format='json', endpoint=None, auth=True):
        endpoint = endpoint or self.detail_endpoint
        data = data or {}
        authentication = self.get_credentials() if auth else None
        return self.api_client.delete(endpoint, format=format, data=data, authentication=authentication)

    def tearDown(self):
        pass

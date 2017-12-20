# -*- coding: utf-8 -*-
# @Author: theo-l
# @Date:   2017-06-26 18:50:57
# @Last Modified by:   theo-l
# @Last Modified time: 2017-06-26 21:40:34

from tastypie.test import ResourceTestCaseMixin
from django.test import TestCase
from django.db.models import Model

from factories import UserFactory


class APIBaseTestCase(ResourceTestCaseMixin, TestCase):
    api_prefix = '/api/v1/'
    resource_name = None

    def setUp(self):
        """
        Prepare some precondition data for each test case
        """
        super(APIBaseTestCase, self).setUp()
        self.more_setup()
        self.setup_endpoints()

    def more_setup(self):
        self.default_user = UserFactory()

    def setup_endpoints(self):
        self.list_endpoint = self.api_prefix + '{}/'.format(self.resource_name)
        self.detail_endpoint = self.api_prefix + '{}/{}/'.format(self.resource_name)

    def tearDown(self):
        super(APIBaseTestCase, self).tearDown()

    ############################################################
    # customized http request util methods
    ############################################################
    def get(self, url, data=None, auth=True, **kwargs):
        """
        Used to do a http get request
        """
        authentication = self.get_credentials(auth)
        return self.api_client.get(url, format=format, data=data, authentication=authentication, **kwargs)

    def post(self, url, data=None, auth=True, **kwargs):
        """
        Used to do a http post request
        """
        authentication = self.get_credentials(auth)
        return self.api_client.post(url, data=data, authentication=authentication, **kwargs)

    def form(self, url, data=None, auth=True, **kwargs):
        """
        Used to do a normal http form request
        """
        authentication = self.get_credentials(auth)
        return self.client.post(url, data=data, HTTP_AUTHORIZATION=authentication, **kwargs)

    def delete(self, url, data=None, auth=True, **kwargs):
        """
        Used to  do a http delete request
        """
        authentication = self.get_credentials(auth)
        return self.api_client.delete(url, data=data, authentication=authentication, **kwargs)

    def patch(self, url, data=None, auth=True, **kwargs):
        authentication = self.get_credentials(auth)
        return self.api_client.patch(url, data=data, authentication=authentication, **kwargs)

    def put(self, url, data=None, auth=True, **kwargs):
        authentication = self.get_credentials(auth)
        self.api_client.put(url, data=data, authentication=authentication, **kwargs)

    ############################################################
    # some util methods using in test case
    ############################################################
    def get_credentials(self, auth=True):
        """
        Generate apikey style Authentication value depends on the auth flag
        """
        return self.create_apikey(username=self.default_user.username,
                                  api_key=self.default_user.api_key.key) if auth else None

    @staticmethod
    def get_random_model_obj(model_class):
        """
        Return a random instance object of the given model class
        """
        if not isinstance(model_class, Model):
            raise ValueError('"model_class" should be the subclass of a "Django Model" class')
        return model_class.enables.order_by('?').first()

    ############################################################
    # more assertion method for tastypie resource api
    ############################################################

    def assertListObjectCount(self, response, count=0, collection_name='objects'):
        """
        Assertion the list api returned the given number of objects
        """
        self.assertHttpOK(response)
        data = self.deserialize(response)
        self.assertEqual(len(data[collection_name]), count)

    def assertKeysInList(self, response, includes=None, excludes=None, collection_name='objects'):
        """
        1. Assertion the given includes(if not none) field in each object of the returned collections
        2.Assertion the given excludes(if not none) field not in each object of the returned collections
        """
        self.assertHttpOK(response)
        data = self.deserialize(response)

        if includes:
            for obj in data[collection_name]:
                for field in includes:
                    self.assertTrue(field in obj)

        if excludes:
            for obj in data[collection_name]:
                for field in excludes:
                    self.assertFalse(field in obj)

    def assertKeysInDetail(self, response, includes=None, excludes=None):
        """
        1. Assertion the given includes(if not none) field in the returned object
        2.Assertion the given excludes(if not none) field not in the returned object
        """
        self.assertHttpOK(response)
        data = self.deserialize(response)

        if includes:
            for field in includes:
                self.assertTrue(field in data)

        if excludes:
            for field in excludes:
                self.assertFalse(field in data)

    def assertItemsInDetail(self, response, items=None):
        """
        Assertion some field:value pairs in the returned detail object
        """
        self.assertHttpOK(response)

        if items:
            data = self.deserialize(response)
            for key, value in items.iteritems():
                self.assertEqual(data[key], value)

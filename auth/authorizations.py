# -*- encoding: utf-8 -*-

from django.contrib.auth import get_user_model
from tastypie.exceptions import Unauthorized
from tastypie.authorization import Authorization

AUTH_MODEL = get_user_model()


class WriteAuthorization(Authorization):
    """
    Customized Authorization for data write actions
    """

    @staticmethod
    def authorization(object_list, bundle):
        """
        Mainly authorize the detail update actions: (post, patch, delete)
        """
        if bundle.request.user.is_authenticated():

            # only user can change its own data
            if isinstance(bundle.obj, AUTH_MODEL) and bundle.request.method in ('POST', 'PUT'):
                return bundle.request.user == bundle.obj

            # update action only allowed the object's creator
            if hasattr(bundle.obj, 'user'):
                return bundle.request.user == bundle.obj

            # Some public data can be edited by any authorized user
            return True

        return False

    def create_list(self, object_list, bundle):
        raise Unauthorized(u'Can not create a list of resource at once!')

    def update_list(self, object_list, bundle):
        raise Unauthorized(u'Can not update a list of resource at once!')

    def delete_list(self, object_list, bundle):
        raise Unauthorized(u'Can not delete a list of resource at once!')

    def create_detail(self, object_list, bundle):
        return self.authorization(object_list, bundle)

    def update_detail(self, object_list, bundle):
        return self.authorization(object_list, bundle)

    def delete_detail(self, object_list, bundle):
        return self.authorization(object_list, bundle)

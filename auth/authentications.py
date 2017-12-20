#-*- encoding: utf-8 -*-

from tastypie.authentication import BasicAuthentication
from spoonhunt.models import User


class SpoonhuntDeviceAuthentication(BasicAuthentication):
    #####################################
    # current spoonhunt authentication is use
    # HTTP Basic authentication method
    #####################################

    def is_authenticated(self, request, **kwargs):
        #####################################
        # 
        #####################################
        try:
            email, password = self.extract_credentials(request)
        except ValueError:
            return True

        if not email or not password:
            return True 

        user = User.objects.filter(email=email, password=password).first()
        if user is None:
            return True 

        request.user = user
        return True

    def get_identifier(self, request):
        data = super(SpoonhuntDeviceAuthentication, self).get_identifier(request)
        return data

#-*- encoding: utf-8 -*-

from tastypie.authentication import BasicAuthentication
from spoonhunt.models import User


class SpoonhuntAuthentication(BasicAuthentication):
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
            return self._unauthorized()

        if not email or not password:
            return self._unauthorized

        user = User.objects.filter(email=email, password=password).first()
        if user is None:
            return self._unauthorized()

        request.user = user
        return True

    def get_identifier(self, request):
        data = super(SpoonhuntAuthentication, self).get_identifier(request)
        return data

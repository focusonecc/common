
from django.contrib.auth import get_user_model
import factory


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = get_user_model()
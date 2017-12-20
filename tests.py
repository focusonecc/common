<<<<<<< HEAD
from django.test import TestCase

# Create your tests here.
=======
class Test:
    @staticmethod
    def static_call(word):
        print 'calling static method: {}'.format(word)


if __name__ == '__main__':
    t = Test()
    t.static_call('hello')
>>>>>>> a1c36b07fbdd3d2c91462ecec37ffa8a83176473

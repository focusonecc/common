class Test:
    @staticmethod
    def static_call(word):
        print 'calling static method: {}'.format(word)


if __name__ == '__main__':
    t = Test()
    t.static_call('hello')

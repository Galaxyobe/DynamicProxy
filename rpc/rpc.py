# -*- coding: utf-8 -*-
import zerorpc


class RPCServer(object):
    def __init__(self, ip, port, methods):
        s = zerorpc.Server(methods)
        try:
            s.bind("tcp://%s:%s" % (ip, port))
            print 'rpc start %s:%s' % (ip, port)
            s.run()
        except Exception, ex:
            print("%s:%s" % (Exception, ex))


class RPCClient(object):

    c = zerorpc.Client()

    def __init__(self, ip, port):
        self.c.connect("tcp://%s:%s" % (ip, port))

    def getClient(self):
        return self.c

    def close(self):
        self.c.close()

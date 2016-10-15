from django.core.cache.backends.memcached import BaseMemcachedCache

import  threading
from django.core.cache.backends.base import BaseCache

import socket
import sys
import re
DATA_LENGTH = 4096

class MyCacheBackend(object):
    """
    Class that works as a client Python binding for a Django Application
    """
    def __init__(self, server, *args, **kwargs):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        hostdata = server.split(':')
        self.ip = hostdata[0]
        self.port = int(hostdata[1])
        self.address = (self.ip, self.port)
        self.s.connect(self.address)

    def _set(self, headers, body):
        '''
        Function that permits new data to be stored in the cache memory
        It is executed for commands that introduce new data in the memory
        :param headers: command header that contains the key, flag and time
        :param body: command body that contains the object to be stored
        :return:
        '''
        self._send_command(headers)
        self._send_command('%s\r\n' % body)
        if self._recv_response() != 'STORED\r\n':
            print >> sys.stderr, '%s' % 'Something went wrong'

    def set(self, key, body, time=0, flag=0, version=None):
        """
        Function to set new value into the cache
        :param key:
        :param body:
        :param time:
        :param flag:
        :param version:
        :return:
        """
        length = len(str(body)) if type(body) is int else len(body)
        headers = 'set %s %s %s %s\r\n' % (key, flag, time, length)
        body = body
        self._set(headers, body)

    def add(self, key, body, time=0, flag=0, version=None):
        """
        Function to add new value into the cache only if it doesn't
        exist already in the cache memory
        :param key:
        :param body:
        :param time:
        :param flag:
        :param version:
        :return:
        """
        length = len(str(body)) if type(body) is int else len(body)
        headers = 'add %s %s %s %s\r\n' % (key, flag, time, length)
        body = body
        self._set(headers, body)

    def replace(self, key, body, time=0, flag=0, version=None):
        """
        Function to replace an object which key is in the cache memory
        :param key:
        :param body:
        :param time:
        :param flag:
        :param version:
        :return:
        """
        length = len(str(body)) if type(body) is int else len(body)
        headers = 'replace %s %s %s %s' % (key, flag, time, length)
        body = body
        self._set(headers, body)

    def get(self, key, default=None, version=None):
        """
        Retrieve object by key from cache memory
        :param key:
        :param default:
        :param version:
        :return:
        """
        self._send_command('get %s' % key)
        data = self._recv_response()
        print >> sys.stderr, '%s' % data
        if data == 'END\r\n':
            return None
        else:
            m = re.match('VALUE (?P<flag>[0-2]) (?:[0-9]+) (?P<obj>.*)\r\nEND',
                         data)
            if not m:
                m = re.match('VALUE (?P<flag>[0-2]) (?:[0-9]+) (?P<obj>[0-9]+)\r\nEND',
                         data)
            newdict = m.groupdict()
            return newdict['obj']

    def delete(self, key, version=None):
        """Delete object by key from cache memory"""
        self._send_command( 'delete %s' % key)
        data = self._recv_response()

    def _send_command(self, command):
        self.s.sendall(command)

    def _recv_response(self):
        return self.s.recv(DATA_LENGTH)

    def disconnect_server(self):
        self.s.close()


mymemcached = MyCacheBackend("127.0.0.1:11212")

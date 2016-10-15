#!/usr/bin/python2

import socket
import sys
import re
import pickle

from multiprocessing import Process, Lock

from cmdhandler import SetHandler, GetHandler
from cmdhandler import AddHandler, ReplaceHandler
from cmdhandler import DeleteHandler

DATA_LENGTH = 4096
HOST = '127.0.0.1'  # Symbolic name, meaning all available interfaces
PORT = 11212  # Arbitrary non-privileged port


def clientthread(conn, sock, lock, cache_mem):

    while True:
        data = conn.recv(DATA_LENGTH)

        # Receiving from client
        if not data:
            break
        else:
            print(repr(data))
            data_list = re.split(' |\r\n', data)

            if data_list[0] == 'quit':
                print("Connection closed")
                conn.shutdown(socket.SHUT_RDWR)
                break
            elif data_list[0] == 'get':

                myh = GetHandler(data_list[1], cache_mem)
                conn.sendall(myh.response_get())

            elif data_list[0] == 'set':

                data = conn.recv(DATA_LENGTH)
                myh = SetHandler(data_list[1], cache_mem)
                print(myh.response_set(data_list[2:6], data))
                print(data)
                conn.sendall(myh.response_set(data_list[2:6], data))
            elif data_list[0] == 'add':

                data = conn.recv(DATA_LENGTH)
                myh = AddHandler(data_list[1], cache_mem)
                conn.sendall(myh.response_add(data_list[2:6], data))

            elif data_list[0] == 'replace':

                data = conn.recv(DATA_LENGTH)
                myh = ReplaceHandler(data_list[1], cache_mem)
                conn.sendall(myh.response_replace(data_list[2:6], data))

            elif data_list[0] == 'delete':

                myh = DeleteHandler(data_list[1], cache_mem)
                print(myh.response_delete())
                conn.send(myh.response_delete())

            else:
                reply = 'OK...' + data
                conn.sendall(reply)


if __name__ == "__main__":

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('Socket created')
    # Bind socket to local host and port
    try:
        s.bind((HOST, PORT))
    except socket.error as msg:
        print('Bind failed. Error Code : ' +
              str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    print('Socket bind complete')
    cache_mem = {}
    cache_filename = 'filename.pkl'
    with open(cache_filename, 'wb') as handle:
                pickle.dump({}, handle)

    while 1:
        # wait to accept a connection - blocking call
        s.listen(10)
        print('Socket now listening')
        conn, addr = s.accept()
        lock = Lock()
        print('Connected with ' + addr[0] + ':' + str(addr[1]))
        p = Process(target=clientthread, args=(conn, s, lock, cache_mem,))
        p.daemon = True
        p.start()
    s.close()

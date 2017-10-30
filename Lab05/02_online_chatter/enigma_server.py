#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Server side for EnigmaChat
'''

import socket
import selectors
import logging
import sys
import json

SERVER_IP = "0.0.0.0"
SERVER_PORT = 7654
RECV_BUFFER = 4096


class ChatServer(object):
    '''
    server class
    '''

    def __init__(self, host, port, buffersize):
        self.buffersize = buffersize
        self.host = host
        self.port = port
        self.connection_list = []
        self.addr = dict()
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket = server_socket
        self.sel = selectors.DefaultSelector()

    def start(self):
        '''
        Initilization and loop of server
        '''
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(10)
        logging.info("Chat server started on port %d", self.port)
        self.sel.register(self.server_socket, selectors.EVENT_READ)
        while 1:
            # get the list sockets which are ready to be read through select
            events = self.sel.select()
            # logging.debug(str(events))
            for key, _ in events:
                sock = key.fileobj
                if sock == self.server_socket:
                    # logging.debug("1")
                    self.accept_conn()
                # a message from a client, not a new connection
                else:
                    #
                    try:
                        self.process_message(sock)
                        # exception
                    except OSError:
                        self.broadcast(sock,
                                       "::Server::offline::%s" % self.addr[sock])
                        continue
        self.server_socket.close()

    def accept_conn(self):
        '''
        a new connection request recieved
        '''
        sockfd, addr = self.server_socket.accept()
        self.connection_list.append(sockfd)
        self.sel.register(sockfd, selectors.EVENT_READ)
        self.addr[sockfd] = '[%s:%s]' %  addr
        sockfd.send(
            ("::Server::json::" + json.dumps(list(self.addr.values()))).encode())
        print(list(self.addr.values()))
        logging.info("Client (%s, %s) connected", *addr)
        self.broadcast(sockfd, "::Server::online::%s" % self.addr[sockfd])

    def process_message(self, sock):
        '''
        process data recieved from client
        '''
        try:
            data = sock.recv(RECV_BUFFER)
        except ConnectionError:
            self.connection_list.remove(sock)
            del self.addr[sock]
            self.sel.unregister(sock)
            logging.info(
                "::Server::offline::Client (%s, %s) disconnected", *self.addr[sock])
            sock.close()
            return
        if data:
            # there is something in the socket
            self.broadcast(
                sock, '%s' % self.addr[sock] + data.decode())
        else:
            # remove the socket that's broken
            # if sock in SOCKET_LIST:
            self.connection_list.remove(sock)
            self.sel.unregister(sock)
            addr = sock.getpeername()
            logging.info("Client (%s, %s) disconnected", *addr)
            # at this stage, no data means probably the connection has been broken
            self.broadcast(sock, "::Server::offline::%s" % self.addr[sock])
            del self.addr[sock]

    def broadcast(self, sock, message):
        '''
        broadcast chat messages to all connected clients
        '''
        for connection in self.connection_list:
            # send the message only to peer
            if connection != self.server_socket and connection != sock:
                try:
                    connection.send(message.encode())
                except OSError:
                    # broken socket connection
                    connection.close()
                    # broken socket, remove it
                    if connection in self.connection_list:
                        self.connection_list.remove(connection)
                        del self.addr[connection]
                        self.sel.unregister(sock)


def main():
    '''
    Main entrance
    '''
    service = ChatServer(SERVER_IP, SERVER_PORT, RECV_BUFFER)
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    service.start()


if __name__ == '__main__':
    main()

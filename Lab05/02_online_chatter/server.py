#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Server side for EnigmaChat
'''

import sys
import socket
import select
import selectors

SERVER_IP = "127.0.0.1"
SERVER_PORT = 7654
RECV_BUFFER = 4096
HOST = ''
SOCKET_LIST = []

def new_connection(connection, mask):
    pass


def chat_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, SERVER_PORT))
    server_socket.listen(10)

    # add server socket object to the list of readable connections
    SOCKET_LIST.append(server_socket)

    print("Chat server started on port %d" % SERVER_PORT)
    sel = selectors.DefaultSelector()
    sel.register(server_socket, selectors.EVENT_READ)
    while 1:

        # get the list sockets which are ready to be read through select
        # 4th arg, time_out  = 0 : poll and never block
        # ready_to_read, ready_to_write, in_error = select.select(
        #    SOCKET_LIST, [], [], 0)
        events = sel.select()
        for key, mask in events:
            #callback = key.data
            #callback(key.fileobj, mask)
            sock =  key.fileobj
            # a new connection request recieved
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                SOCKET_LIST.append(sockfd)
                sel.register(sockfd, selectors.EVENT_READ)
                print("Client (%s, %s) connected" % addr)
                broadcast(server_socket, sockfd,
                          "[%s:%s] entered our chatting room\n" % addr)

            # a message from a client, not a new connection
            else:
                # process data recieved from client,
                try:
                    # receiving data from the socket.
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        # there is something in the socket
                        broadcast(server_socket, sock, "\r" +
                                  '[' + str(sock.getpeername()) + '] ' + data.decode())
                    else:
                        # remove the socket that's broken
                        # if sock in SOCKET_LIST:
                        SOCKET_LIST.remove(sock)
                        sel.unregister(sock)
                        # at this stage, no data means probably the connection has been broken
                        broadcast(server_socket, sock,
                                  "Client (%s, %s) is offline\n" % addr)

                # exception
                except OSError:
                    broadcast(server_socket, sock,
                              "Client (%s, %s) is offline\n" % addr)
                    continue

    server_socket.close()

# broadcast chat messages to all connected clients


def broadcast(server_socket, sock, message):
    for connection in SOCKET_LIST:
        # send the message only to peer
        if connection != server_socket and connection != sock:
            try:
                connection.send(message.encode())
            except OSError:
                # broken socket connection
                connection.close()
                # broken socket, remove it
                if connection in SOCKET_LIST:
                    SOCKET_LIST.remove(connection)


if __name__ == "__main__":

    sys.exit(chat_server())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
This is a socket implementation of http server
'''
# Import socket module
from socket import socket
from socket import AF_INET
from socket import SOCK_STREAM
from socket import SOL_SOCKET, SO_REUSEADDR
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import os

# Put in your codes here to create a TCP sever socket
# and bind it to your server address and port number
HOST, PORT_NUM = "127.0.0.1", 1024

CLRF = '\r\n'


class Request(object):
    '''
    A simple http request object"
    '''

    def __init__(self, raw_request):
        self._raw_request = raw_request

        self._method, self._path, self._protocol, self._headers = self.parse_request()

    def getpath(self):
        '''
        return the url path
        '''
        if self._path == "/":
            # default index.html
            self._path = "/index.html"
        return self._path, self.start_byte

    def parse_request(self):
        '''
        trun request into structured data
        '''
        temp = [i.strip() for i in self._raw_request.splitlines()]
        self.start_byte = -1
        if -1 == temp[0].find('HTTP'):
            raise Exception('Incorrect Protocol')

        # Extract the range part of http request
        if -1 != self._raw_request.find('\r\nRange'):
            import re
            # print(self._raw_request)
            # r"Range: bytes=(\d*)-(\d*)"
            re_result = re.search(
                r"Range: bytes=(\d*)-(\d*)", self._raw_request)
            # print(re_result)
            if re_result != None:
                # print(re_result.group(1), re_result.group(2))
                self.start_byte = int(re_result.group(1))

        # Figure out our request method, path, and which version of HTTP we're using
        method, path, protocol = [i.strip() for i in temp[0].split()]

        # Create the headers, but only if we have a GET reqeust
        headers = {}
        if method == "GET":
            for k, value in [i.split(':', 1) for i in temp[1:-1]]:
                headers[k.strip()] = value.strip()
        else:
            raise Exception('Only accepts GET requests')

        return method, path, protocol, headers

    def __repr__(self):
        return repr({'method': self._method, 'path': self._path,
                     'protocol': self._protocol, 'headers': self._headers})


class Response(object):
    '''
    Process the response of http
    '''

    def __init__(self, filedes):
        self.status = 200
        self.offset = 0
        # Range request and partial responce if filedes>=0
        if filedes[1] >= 0:
            self.status = 206
            self.offset = filedes[1]
        try:
            self.file = open('.' + filedes[0], mode='rb')
            self.filename = '.' + filedes[0]
        except IOError:
            self.status = 404
            self.file = open('./Err404.html', mode='rb')
            self.filename = './Err404.html'
        finally:
            self.filelen = int(os.stat(self.filename).st_size)
            # print(self.filelen, self.not_found)

    def get_resp_header(self):
        '''
        return the http header
        '''
        # get fommated time
        now = datetime.now()
        stamp = mktime(now.timetuple())
        timestr = format_date_time(stamp)

        # 404 header
        if self.status == 404:
            header = "HTTP/1.1 404 Not Found\r\n" + \
                "Server: nginx\r\n" +\
                "Date: %s\r\n" % timestr +\
                "Content-Type: text/html\r\n" +\
                "Content-Length: %d\r\n" % self.filelen +\
                "Connection: keep-alive\r\n\r\n"
            return header
        if self.status == 200:
            # 200 OK header
            header = "HTTP/1.1 200 OK\r\n" +\
                "Date: %s\r\n" % timestr +\
                "Server: nginx\r\n" +\
                "Last-Modified: %s\r\n" % timestr +\
                "Accept-Ranges: bytes\r\n" +\
                "Content-Length: %d\r\n" % self.filelen +\
                "Keep-Alive: timeout=5, max=100\r\n" +\
                "Connection: Keep-Alive\r\n" +\
                "Content-Type: %s; charset=UTF-8\r\n\r\n" % self.get_content_type()
            return header

        if self.status == 206:
            header = "HTTP/1.1 206 Partial Content\r\n" +\
                "Accept-Ranges: bytes\r\n" +\
                "Content-Range: bytes %d-%d/%d\r\n" \
                % (self.offset, self.filelen - 1, self.filelen) +\
                "Content-Length: %d\r\n" % (self.filelen - self.offset) +\
                "Content-Type: %s\r\n\r\n" % self.get_content_type()
            return header

    def get_content_type(self):
        '''
        Use built in function to get filetype and map them
        '''
        _, extension = os.path.splitext(self.filename)
        mapping = {'html': 'text/html', 'htm': 'text/html', 'txt': 'text/plain',
                   'mp4': 'video/mp4', 'ogg': 'audio/ogg', 'mp3': 'audio/mpeg', 'jpg': 'image/jpeg'}
        print(extension)
        if extension[1:] in mapping.keys():
            return mapping[extension[1:]]
        else:
            return 'text/plain'

    def send_file(self, connection):
        '''
        send the main body
        '''
        if self.status == 404:
            return
        # Send HTTP content body
        if self.offset <= self.filelen:
            self.file.seek(self.offset)
        else:
            return
        buff = self.file.read(1024)
        total = 0
        while buff:
            total += len(buff)
            try:
                connection.send(buff)
            except BrokenPipeError as err:
                print("Detected remote disconnect", err)
                break
            buff = self.file.read(1024)
        print(total, self.filename)
        self.file.close()
        return


def main():
    '''
    main entrance
    '''
    # (SOCK_STREAM) is used for TCP
    server_socket = socket(AF_INET, SOCK_STREAM)
    try:
        # Bind the socket to server address and server port
        #server_socket.bind((HOST, PORT_NUM))
        server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server_socket.bind(('192.168.111.147', 1024))
        server_socket.listen(10)
    except OSError:
        print("Port number in use. Exiting....")
        exit()
    # Server should be up and running and listening to the incoming connections
    try:
        while True:
            connection_socket = None
            # If an exception occurs during the execution of try clause
            # the rest of the clause is skipped
            # If the exception type matches the word after except
            # the except clause is executed
            try:
                print('Ready to serve...')
                # Set up a new connection from the client
                connection_socket, addr = server_socket.accept()
                # Receives the request message from the client
                # connection-oriented
                # For best match with hardware and network realities
                # the value of bufsize should be a relatively small power of 2
                # for example, 4096.
                http_request = connection_socket.recv(1024).decode()
                # print(http_request)
                http_request = Request(http_request)
                # print(repr(http_request), http_request.getpath())
                resp = Response(http_request.getpath())
                print("Request from %s, path: %s" %
                      (addr, http_request.getpath()))
                header = resp.get_resp_header()
                # print(header)
                connection_socket.send(header.encode())
                resp.send_file(connection_socket)
            finally:
                if connection_socket:
                    connection_socket.close()
    finally:
        # Put your code here to close the socket
        server_socket.close()


if __name__ == "__main__":
    main()

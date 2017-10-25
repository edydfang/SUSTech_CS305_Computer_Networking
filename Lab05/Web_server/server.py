#! /usr/bin/env python3
'''
This is a socket implementation of http server
'''
# Import socket module
from socket import socket
from socket import AF_INET
from socket import SOCK_STREAM
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime

# Put in your codes here to create a TCP sever socket
# and bind it to your server address and port number
HOST, PORT_NUM = "127.0.0.1", 1025

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
        return self._path

    def parse_request(self):
        '''
        trun request into structured data
        '''
        temp = [i.strip() for i in self._raw_request.splitlines()]
        if -1 == temp[0].find('HTTP'):
            raise Exception('Incorrect Protocol')

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
        return repr({'method': self._method, 'path': self._path, 'protocol': self._protocol, 'headers': self._headers})

class Response(object):
    def __init__(self, filename):
        self.filename = filename
        self.not_found = False
        try:
            self.file = open('.'+filename,mode='r')
        except IOError:
            self.not_found = True

    def get_resp_header(self):
        if self.not_found:
            header = '''
            HTTP/1.1 404 Not Found
            Server: nginx
            Date: Wed, 25 Oct 2017 18:16:34 GMT
            Content-Type: text/html
            Content-Length: 479
            Connection: keep-alive
            '''
            return header

        now = datetime.now()
        stamp = mktime(now.timetuple())
        # format_date_time(stamp)
        header = '''
        HTTP/1.1 %s
        Date: %d
        Server: nginx
        Last-Modified: %d
        Accept-Ranges: bytes
        Content-Length: %d
        Keep-Alive: timeout=5, max=100
        Connection: Keep-Alive
        Content-Type: text/plain; charset=UTF-8\r\n
        '''
        return header

    def send_file(self):
        if self.not_found:
            # Send HTTP response message for file not found
            pass
        else:
            pass


def main():
    '''
    main entrance
    '''
    # (SOCK_STREAM) is used for TCP
    server_socket = socket(AF_INET, SOCK_STREAM)
    try:
        # Bind the socket to server address and server port
        server_socket.bind((HOST, PORT_NUM))
        server_socket.listen(10)
    except OSError:
        print("Port number in use. Exiting....")
        exit()
    # Server should be up and running and listening to the incoming connections
    try:
        while True:
            try:
                print('Ready to serve...')
                # Set up a new connection from the client
                connection_socket, _ = server_socket.accept()
                # If an exception occurs during the execution of try clause
                # the rest of the clause is skipped
                # If the exception type matches the word after except
                # the except clause is executed
                
                # Receives the request message from the client
                # connection-oriented
                # For best match with hardware and network realities
                # the value of bufsize should be a relatively small power of 2
                # for example, 4096.
                http_request = connection_socket.recv(1024).decode()
                # print(http_request)
                http_request = Request(http_request)
                print(repr(http_request), http_request.getpath())
                resp = Response(http_request.getpath())
                header = resp.get_resp_header()
                print(header)
                connection_socket.send(header)
                resp.send_file()
            finally:
                connection_socket.close()
    finally:
        # Put your code here to close the socket
        server_socket.close()


if __name__ == "__main__":
    main()

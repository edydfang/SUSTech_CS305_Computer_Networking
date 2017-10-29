# Lab Assignment Description

## Assignment 01 Simple Web server

### Requirements

In this assignment, you will develop a simple Web server in Python that is capable of processing only one request. Specifically, your Web server will

- create a connection socket when contacted by a client (browser);
- receive the HTTP request from this connection;
- parse the request to determine the specific file being requested;
- get the requested file from the server’s file system;
- create an HTTP response message consisting of the requested file preceded by header lines; and
- send the response over the TCP connection to the requesting browser.

If a browser requests a file that is not present in your server, your server should return a “404 Not Found” error message. In the companion Web site, we provide the skeleton code for your server. Your job is to complete the code, run your server, and then test your server by sending requests from browsers running on different hosts. If you run your server on a host that already has a Web server running on it, then you should use a different port than port 80 for your Web server

### Additional Requirements

- Ability to display text with Chinese and English at the same time
- Multimedia including images, video and music

### Reference

- [Python-filestate](https://docs.python.org/2/library/os.html#os.stat)
- [rfc-7230](https://tools.ietf.org/html/rfc7230)
- [Python Pipebroken Exception](https://docs.python.org/3/library/exceptions.html#OSError)
- [How to handle a broken pipe (SIGPIPE) in python?](https://stackoverflow.com/questions/180095/how-to-handle-a-broken-pipe-sigpipe-in-python/180922#180922)
- [206 PARTIAL CONTENT](https://httpstatuses.com/206)
- [HTML Demo](https://www.w3schools.com/)

## Assignment 02 An online chat program

### Requirements

- Real-time message sending and displaying
- Display the sender
- Multithread
- UDP

### Additional Requirements

- client - client or client - server
- Graphic User Interface

### Reference

- [Tkinker Book](http://effbot.org/tkinterbook/)
- [GUI POLLING](http://effbot.org/tkinterbook/widget.htm#Tkinter.Widget.after-method)
- [select — Waiting for I/O completion](https://docs.python.org/3.6/library/select.html)
- [selectors — High-level I/O multiplexing](https://docs.python.org/3.6/library/selectors.html#module-selectors)
- [NETWORK PROGRAMMING II - CHAT SERVER & CLIENT](http://www.bogotobogo.com/python/python_network_programming_tcp_server_client_chat_server_chat_client_select.php)
- [Python threads: communication and stopping](https://eli.thegreenplace.net/2011/12/27/python-threads-communication-and-stopping)



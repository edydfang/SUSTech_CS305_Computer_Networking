#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
A GUI chat program based on UDP protocal
'''

import tkinter as tk
from tkinter import Text, Listbox, Frame
from tkinter import Label, Entry, NORMAL, END, Button
from tkinter import E, S, W, N, DISABLED
import socket
import selectors
import re
import threading
import queue
import json

# Base windows size ratio
WIDTH_HEIGHT_RATIO = 0.9


class Chatwindows(tk.Tk):
    '''
    Main Chat window
    '''

    def __init__(self, input_q, output_q):
        super().__init__()
        self.update_scaling_unit()
        # self.adjust_size()
        self.title("EnigmaChat")
        self.frame = Frame(self)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.frame.grid(row=0, column=0, sticky=N + S + E + W)
        self.organize_widgets(self.frame)
        self.input_q = input_q
        self.output_q = output_q
        self.resizable(width=False, height=False)
        self.listlen = 0

    def organize_widgets(self, frame):
        '''
        initialize the widgets
        '''
        self.chatbox = Text(frame, height=20, width=35, font=12)
        self.chatbox.grid(row=0, column=0, sticky=N + S + E + W)
        self.chatbox.config(state=DISABLED)
        self.chatbox.tag_config('INFO', foreground='blue')
        self.chatbox.tag_config('ERROR', foreground='red')
        # svar = StringVar()
        # svar.trace("w", lambda name, index, mode, sv=svar: self.messagebox_onchange(sv))
        self.messagebox = Text(frame, height=5, width=35, font=12)
        self.messagebox.grid(row=1, column=0, sticky=N + S + E + W)
        # self.messagebox.bind('<<Modified>>', self.messagebox_onchange)

        self.listbox = Listbox(frame, font=12, width=20)
        self.listbox.grid(row=0, column=1, rowspan=2, sticky=N + S + E + W)
        self.sendbutton = Button(
            frame, text="Send", command=self.send_message, font=12, width=5, height=1)
        self.sendbutton.grid(row=2, column=0)
        self.sendbutton.config(state=DISABLED)
        self.serverentry = Entry(frame, width=18, font=8)
        self.serverentry.insert(END, '127.0.0.1:7654')
        self.serverentry.grid(row=3, column=0, sticky=W)
        self.connbutton = Button(
            frame, text="Connect", font=8, width=10, height=1, command=self.connect)

        self.connbutton.grid(row=3, column=0, sticky=E)

        # self.statusbar = Message(
        #     frame, text='Ready to Connect')
        # self.statusbar.grid(row=2, rowspan=2, column=1)

        frame.rowconfigure(0, weight=10)
        frame.rowconfigure(1, weight=2)
        frame.rowconfigure(2, weight=1)
        frame.columnconfigure(0, weight=2)
        frame.columnconfigure(1, weight=3)

    def update_scaling_unit(self):
        '''
        get current windows resolution
        '''
        # Get screen size
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Make a scaling unit, this is bases on average percentage from
        # width and height.
        self.width_unit = screen_width / 100
        self.height_unit = screen_height / 100

    def adjust_size(self):
        '''
        resize the windows
        '''
        height = int(50 * self.height_unit)
        width = int(50 * self.height_unit) * WIDTH_HEIGHT_RATIO
        self.geometry("%dx%d" % (width, height))
        self.minsize(width=width, height=width)

    def update(self):
        '''
        the main polling function the communicate with client
        '''
        if not self.output_q.empty():
            inputinfo = self.output_q.get(True, 0.5)
            if inputinfo['cmd'] == 1:
                self.add_chat_record(inputinfo['body'])
            elif inputinfo['cmd'] == 0:
                self.add_system_record(1, inputinfo['body'])
            # connect successfully
            elif inputinfo['cmd'] == 2:
                self.connbutton.config(state=DISABLED)
                self.sendbutton.config(state=NORMAL)
            # print(inputinfo)
            elif inputinfo['cmd'] == 4:
                self.update_list(inputinfo['body'])

        self.after(20, self.update)

    def add_chat_record(self, message):
        '''
        add message to chatbox
        '''
        self.chatbox.config(state=NORMAL)
        self.chatbox.insert(END, message.strip() + '\n')
        self.chatbox.config(state=DISABLED)
        self.chatbox.see(END)

    def add_system_record(self, infotype, info):
        '''
        the system info display
        '''
        self.chatbox.config(state=NORMAL)
        if infotype == 1:
            self.chatbox.insert(END, "INFO:" + info.strip() + '\n', 'INFO')
        else:
            self.chatbox.insert(END, "BUG:" + info.strip() + '\n', 'BUG')
        self.chatbox.config(state=DISABLED)
        self.chatbox.see(END)

    def send_message(self):
        '''
        send message through the queue
        '''
        message = self.messagebox.get("1.0", END)
        if message != '':
            self.input_q.put({'cmd': 0, 'body': message})
            self.messagebox.delete('1.0', END)

    def connect(self):
        '''
        send connect command to the queue
        '''
        # self.statusbar.config(text="Connecting")
        self.input_q.put({'cmd': 1, 'body': self.serverentry.get()})

    def update_list(self, clientlist):
        '''
        update the online user list
        '''
        # print("update list")
        self.listbox.delete(0, END)
        for i, item in enumerate(clientlist):
            self.listbox.insert(i + 1, item)
        self.listlen = len(clientlist)


class Client(threading.Thread):
    '''
    the thread dealing with internet connection
    '''
    def __init__(self, input_q, output_q):
        super(Client, self).__init__()
        # input 0 send message 1 connect server 2 receive message 3 server info
        self.input_q = input_q
        # output 0 change status 1 add message 2 connect successfully 3 connection fail
        self.output_q = output_q
        self.stoprequest = threading.Event()
        self.server_host = None
        self.server_port = None
        self.sock = None
        self.sel = None
        self.msg_to_send = queue.Queue()
        self.sender = None
        self.receiver = None
        self.clientlist = None

    def run(self):
        '''
        # As long as we weren't asked to stop, try to take new tasks from the
        # queue. The tasks are taken with a blocking 'get', so no CPU
        # cycles are wasted while waiting.
        # Also, 'get' is given a timeout, so stoprequest is always checked,
        # even if there's nothing in the queue.
        '''
        while not self.stoprequest.isSet():
            try:
                inputinfo = self.input_q.get(True, 0.5)
                # print(inputinfo)
                self.process_input(inputinfo)
                # filenames = list(self._files_in_dir(dirname))
                # self.result_q.put((self.name, dirname, filenames))
            except queue.Empty:
                continue

    def join(self, timeout=None):
        self.sender.join()
        self.receiver.join()
        self.sock.close()
        self.stoprequest.set()
        super(Client, self).join(timeout)

    def process_input(self, inputinfo):
        '''
        preprocess of connection input and connect the server
        '''
        # send a message
        if inputinfo['cmd'] == 0:
            self.msg_to_send.put(inputinfo['body'])
            self.update_message("[ME] %s" % inputinfo['body'])
        # from GUI, connect server
        elif inputinfo['cmd'] == 1:
            # self.server_host = '127.0.0.1'
            # self.server_port = 7654
            re_result = re.search(
                r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})$", inputinfo['body'])
            if re_result == None:
                self.update_status("Wrong IP or Port!")
                return
            else:
                self.server_host = re_result.group(1)
                self.server_port = int(re_result.group(2))
            self.__connect()
        # from receiver, receive new message
        elif inputinfo['cmd'] == 2:
            self.update_message(inputinfo['body'])
        elif inputinfo['cmd'] == 3:
            self.process_server_info(inputinfo['body'])

    def process_server_info(self, msg):
        '''
        process the message from the server
        '''
        # print(msg)
        if msg[0:3] == 'off':
            self.clientlist.remove(msg[9:])
            self.update_status("%s offline" % msg[9:])
        elif msg[0:3] == 'onl':
            self.clientlist.append(msg[8:])
            self.update_status("%s online" % msg[8:])
        elif msg[0:3] == 'jso':
            self.clientlist = json.loads(msg[6:])
        self.output_q.put({'cmd': 4, 'body': self.clientlist})
        # print(self.clientlist)

    def update_status(self, message):
        '''
        push status update to the queue
        '''
        self.output_q.put({'cmd': 0, 'body': message})

    def update_message(self, message):
        '''
        push new message to the queue
        '''
        self.output_q.put({'cmd': 1, 'body': message})

    def __connect(self):
        '''
        connect to the server and run two threads for sending and receiving messages
        '''
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(2)
        self.sel = selectors.DefaultSelector()
        self.sel.register(self.sock, selectors.EVENT_READ)
        # connect to remote host
        try:
            self.sock.connect((self.server_host, self.server_port))
            self.sender = Sender(self.sock, self.msg_to_send)
            self.sender.start()
            self.receiver = Receiver(self.sel, self.input_q)
            self.receiver.start()
        except OSError:
            self.update_status('Unable to connect')
            self.output_q.put({'cmd': 4})
            return
        self.update_status('Connect_successfully')
        self.output_q.put({'cmd': 2})
        # print('Connected to remote host. You can start sending messages')


class Sender(threading.Thread):
    '''
    thread for sending messages
    '''
    def __init__(self, sock, input_queue):
        super(Sender, self).__init__()
        self.sock = sock
        self.input_q = input_queue
        self.stoprequest = threading.Event()

    def run(self):
        while not self.stoprequest.isSet():
            try:
                inputinfo = self.input_q.get(True, 0.5)
                # print("sender:", inputinfo)
                self.sock.send(inputinfo.encode())
            except queue.Empty:
                continue

    def join(self, timeout=None):
        self.stoprequest.set()
        super(Sender, self).join(timeout)


class Receiver(threading.Thread):
    '''
    thread for receiving messages
    '''
    def __init__(self, sel, queue):
        super(Receiver, self).__init__()
        self.sel = sel
        self.output_q = queue
        self.stoprequest = threading.Event()

    def run(self):
        while not self.stoprequest.isSet():
            events = self.sel.select(timeout=0.5)
            for key, _ in events:
                sock = key.fileobj
                # incoming message from remote server, s
                data = sock.recv(4096)
                if not data:
                    self.output_q.put(
                        {'cmd': 3, 'body': 'Disconnected from chat server'})
                    self.stoprequest.set()
                else:
                    # print data
                    # print("received:", (data.decode()))
                    inputmsg = data.decode()
                    if inputmsg[0:10] == '::Server::':
                        self.output_q.put({'cmd': 3, 'body': inputmsg[10:]})
                    else:
                        self.output_q.put({'cmd': 2, 'body': inputmsg})

    def join(self, timeout=None):
        self.stoprequest.set()
        super(Receiver, self).join(timeout)


def main():
    '''
    main entrance
    '''
    inputq = queue.Queue()
    displayq = queue.Queue()
    window = Chatwindows(inputq, displayq)
    # host = '127.0.0.1'
    # port = 7654
    # client = Client(host,port)
    # client.connect()
    # client.listening()
    thread = Client(inputq, displayq)
    thread.start()
    window.after(0, window.update)
    window.mainloop()
    thread.join()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
A GUI chat program based on UDP protocal
'''

import tkinter as tk
from tkinter import Message, Text, Listbox, Frame
from tkinter import Label, Entry, StringVar, END, Button
from tkinter import E, S, W, N, SE, NE, SW, NW, BOTH, DISABLED
import socket
import selectors
import sys
import threading
import queue

# Base windows size ratio
WIDTH_HEIGHT_RATIO = 0.9


class Chatwindows(tk.Tk):
    '''
    Main Chat window
    '''

    def __init__(self, input_q, display_q):
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
        self.display_q = display_q
        self.resizable(width=False, height=False)

    def organize_widgets(self, frame):
        '''
        initialize the widgets
        '''
        self.chatbox = Text(frame, height=20, width=35, font=12)
        self.chatbox.grid(row=0, column=0, sticky=N + S + E + W)
        self.chatbox.config(state=DISABLED)

        #svar = StringVar()
        #svar.trace("w", lambda name, index, mode, sv=svar: self.messagebox_onchange(sv))
        self.messagebox = Text(frame, height=5, width=35, font=12)
        self.messagebox.grid(row=1, column=0, sticky=N + S + E + W)
        # self.messagebox.bind('<<Modified>>', self.messagebox_onchange)

        self.listbox = Listbox(frame, font=12, width=20)
        self.listbox.grid(row=0, column=1, rowspan=2, sticky=N + S + E + W)
        self.sendbutton = Button(
            frame, text="Send", command=self.send_message, font=12, width=5, height=1)
        self.sendbutton.grid(row=2, column=0)

        self.serverentry = Entry(frame, width=18, font=8)
        self.serverentry.insert(END, '127.0.0.1:7654')
        self.serverentry.grid(row=3, column=0, sticky=W)
        self.connbutton = Button(
            frame, text="Connect", font=8, width=10, height=1, command=self.connect)
        self.connbutton.grid(row=3, column=0, sticky=E)

        self.statusbar = Message(
            frame, text='Ready to Connect', font=10, aspect=350)
        self.statusbar.grid(row=2, rowspan=2, column=1)

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
        self.chatbox.insert(END, 'test\n')
        # self.after(1000, self.update)

    def send_message(self):
        message = self.messagebox.get("1.0", END)
        if message != '':
            self.input_q.put({'cmd': 0, 'body': message})
            self.messagebox.delete('1.0', END)

    def connect(self):
        self.statusbar.config(text="Connecting")
        self.input_q.put({'cmd': 1, 'body': self.serverentry.get()})


class Client(threading.Thread):
    '''
    the thread dealing with internet connection
    '''

    def __init__(self, input_q, output_q):
        super(Client, self).__init__()
        self.input_q = input_q
        self.output_q = output_q
        self.stoprequest = threading.Event()
        self.server_host = None
        self.server_port = None
        self.sock = None
        self.sel = None
        self.msg_to_send = queue.Queue()
        self.sender = None
        self.receiver = None
        self.count = 0

    def run(self):
        # As long as we weren't asked to stop, try to take new tasks from the
        # queue. The tasks are taken with a blocking 'get', so no CPU
        # cycles are wasted while waiting.
        # Also, 'get' is given a timeout, so stoprequest is always checked,
        # even if there's nothing in the queue.
        while not self.stoprequest.isSet():
            try:
                inputinfo = self.input_q.get(True, 0.5)
                print(inputinfo)
                self.process_input(inputinfo)
                #filenames = list(self._files_in_dir(dirname))
                #self.result_q.put((self.name, dirname, filenames))
            except queue.Empty:
                continue

    def join(self, timeout=None):
        self.sender.join()
        self.receiver.join()
        self.sock.close()
        self.stoprequest.set()
        super(Client, self).join(timeout)

    def process_input(self, inputinfo):
        # send a message
        if inputinfo['cmd'] == 0:
            self.msg_to_send.put(inputinfo['body'])
        elif inputinfo['cmd'] == 1:
            self.server_host = '127.0.0.1'
            self.server_port = 7654
            self.__connect()
        elif inputinfo['cmd'] == 2:
            pass

    def update_status(self, message):
        self.output_q.put({'cmd': 0, 'body': message})

    def update_message(self, message):
        self.output_q.put({'cmd': 1, 'body': message})

    def __connect(self):
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
            print('Unable to connect')
            return
        print('Connected to remote host. You can start sending messages')


class Sender(threading.Thread):
    def __init__(self, sock, queue):
        super(Sender, self).__init__()
        self.sock = sock
        self.input_q = queue
        self.stoprequest = threading.Event()

    def run(self):
        while not self.stoprequest.isSet():
            try:
                inputinfo = self.input_q.get(True, 0.5)
                #print("sender:", inputinfo)
                self.sock.send(inputinfo.encode())
            except queue.Empty:
                continue

    def join(self, timeout=None):
        self.stoprequest.set()
        super(Sender, self).join(timeout)


class Receiver(threading.Thread):
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
                    print('\nDisconnected from chat server')
                else:
                    # print data
                    # print("received:", (data.decode()))
                    self.output_q.put({'cmd': 2, 'body': data.decode()})

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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
A GUI chat program based on UDP protocal
'''

import tkinter as tk
from tkinter import Message, Text, Listbox, Frame
from tkinter import Label, Entry, Checkbutton, PhotoImage, Button
from tkinter import E, S, W, N, SE, NE, SW, NW, BOTH, DISABLED

# Base windows size ratio
WIDTH_HEIGHT_RATIO = 0.9


class Chatwindows(tk.Tk):
    '''
    Main Chat window
    '''
    def __init__(self):
        super().__init__()
        self.update_scaling_unit()
        # self.adjust_size()
        self.title("EnigmaChat")
        self.frame = Frame(self)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.frame.grid(row=0, column=0, sticky=N+S+E+W)
        self.organize_widgets(self.frame)

    def organize_widgets(self, frame):
        '''
        initialize the widgets
        '''
        self.chatbox = Text(frame, height=20, width=40, font=12)
        self.chatbox.grid(row=0, column=0, sticky=N+S+E+W)
        self.chatbox.config(state=DISABLED)
        self.messagebox = Text(frame, height=5, width=40, font=12)
        self.messagebox.grid(row=1, column=0, sticky=N+S+E+W)
        self.listbox = Listbox(frame)
        self.listbox.grid(row=0, column=1, rowspan=2, sticky=N+S+E+W)
        self.sendbutton = Button(frame, text="Send", font=12, width=10, height=1)
        self.sendbutton.grid(row=2, column=0)
        frame.rowconfigure(0, weight=10)
        frame.rowconfigure(1, weight=2)
        frame.rowconfigure(2, weight=1)
        frame.columnconfigure(0, weight=5)
        frame.columnconfigure(1, weight=2)


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

def main():
    '''
    main entrance
    '''
    window = Chatwindows()
    window.mainloop()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
'''
StudentList
'''

import sys


class StudentList(object):
    '''
    A student list class
    to store the information of student name and ID
    '''

    def __init__(self):
        '''
        use id as key to store the infomation
        '''
        self.studen_list = dict()

    def add_student(self, std_id, name):
        '''
        add student info
        '''
        if id not in self.studen_list.keys():
            self.studen_list[std_id] = name
        else:
            print("duplicated student id! ignored.", file=sys.stderr)

    def print_list(self):
        '''
        print the info
        '''
        for stdid, stdname in sorted(self.studen_list.items()):
            print(stdid, stdname)


class StudentList15(StudentList):
    '''
    subclass of the StudentList
    '''

    def print_list(self):
        '''
        print the info in decending order
        '''
        for stdid, stdname in sorted(self.studen_list.items(), reverse=True):
            print(stdid, stdname) 

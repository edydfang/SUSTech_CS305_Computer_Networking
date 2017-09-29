#!/usr/bin/env python3
'''
Textprocess
'''


class Textprocessor(object):
    '''
    A processor for a specific file
    '''

    def __init__(self, filename):
        '''
        store the file name
        '''
        self.filename = filename

    def read_print_all(self):
        '''
        function01
        '''
        with open(self.filename, 'r') as filed:
            print(filed.read())

    def append_text(self, appended_str):
        '''
        append text at the end of the file
        '''
        with open(self.filename, mode='a') as filed:
            filed.write(appended_str)

    def edit_text(self, index, new_string):
        '''
        edit text at a specific position
        '''
        fileid = open(self.filename, mode='r+')
        max_offset = fileid.seek(0, 2)
        if index + len(new_string) > max_offset:
            print("Error, index or string length exceeds the maxmimum!")
            return
        else:
            try:
                fileid.seek(index)
                fileid.write(new_string)
            except OSError:
                print("Oops! Write permission denied!")
        fileid.close()

    def delete_text(self, index, length):
        '''
        delete a specific length from the index
        '''
        fileid = open(self.filename, mode='r+')
        max_offset = fileid.seek(0, 2)
        if index + length > max_offset or index < 0:
            print("Error, index or string length exceeds the maxmimum or minimum!")
            return
        fileid.seek(0)
        tmp1 = fileid.read(index)
        fileid.seek(index + length)
        tmp2 = fileid.read()
        fileid.close()
        try:
            fileid = open(self.filename, mode='w')
            fileid.write(tmp1)
            fileid.write(tmp2)
        except IOError:
            print("Oops! Write permission denied!")
        fileid.close()


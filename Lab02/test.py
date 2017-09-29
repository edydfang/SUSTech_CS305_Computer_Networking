#!/usr/bin/env python3
'''
test all the class and function
'''
import unittest
from StudentList import StudentList, StudentList15


class TestStudentList(unittest.TestCase):
    '''
    Test all
    '''

    def test_student_list(self):
        '''
        test
        '''
        stl = StudentList()
        stl.add_student(11510493, 'Edward FANG')
        stl.add_student(11610001, 'Alice')
        stl.add_student(11510001, 'Nancy')
        stl.add_student(11510001, 'Nancy')
        stl.add_student(11510002, 'Nancy1')
        stl.print_list()
 

    def test_student_list15(self):
        '''
        test
        '''
        stl = StudentList15()
        stl.add_student(11510493, 'Edward FANG')
        stl.add_student(11610001, 'Alice')
        stl.add_student(11510001, 'Nancy')
        stl.add_student(11510001, 'Nancy')
        stl.add_student(11510002, 'Nancy1')
        stl.print_list()
 


if __name__ == "__main__":
    unittest.main()

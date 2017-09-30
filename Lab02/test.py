#!/usr/bin/env python3
'''
test all the class and function
'''
import unittest
from StudentList import StudentList, StudentList15
from Textprocessor import Textprocessor
from NetworkSolution import NetworkSolution


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

    def test_file_processor(self):
        '''
        test
        '''
        textprocessor = Textprocessor("test.txt")
        textprocessor.append_text("abcdefghijk")
        textprocessor.read_print_all()
        textprocessor.delete_text(7, 4)
        textprocessor.read_print_all()
        textprocessor.edit_text(0, "sustech")
        textprocessor.read_print_all()

    def test_solution3(self):
        '''
        question3
        filesize: 160MB
        '''
        solutioninst = NetworkSolution(160e6 * 8)
        print(solutioninst.get_answer1(),
              solutioninst.get_answer2(), solutioninst.get_answer3())


if __name__ == "__main__":
    unittest.main()

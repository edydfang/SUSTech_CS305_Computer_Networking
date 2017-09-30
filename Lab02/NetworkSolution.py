#!/usr/bin/env python3
'''
a class to solve the question 3
'''


class NetworkSolution(object):
    '''
    Suppose two hosts, A and B, are separated by 50,000 kilometers and are
    connected by a direct link of R=2Gbps. Suppose the propagation speed
    over the link is 2*10^8 meters/sec.
    '''

    def __init__(self, x):
        '''
        input file size: x bits
        '''
        self.filesize = x

    def get_answer1(self):
        '''
        1. Consider sending a file of x bits from Host A to Host B. Suppose the
    file is sent continuously as one big message. What is the maximum
    number of bits that will be in the link at any given time?
        propagation time = (5e4)/(2e8/1e3) sec
        maxbits = 2G * propagation time = 2e9*0.25 = 5e8
        '''
        if self.filesize>5e8:
            return 5e8
        else:
            return self.filesize

    def get_answer2(self):
        '''
        2. What is the width (in meters) of a bit in the link?
        maxbits/length = 5e8/5e7 = 10
        '''
        return 10

    def get_answer3(self):
        '''
        3. How long does it take to send the file, assuming it is sent
continuously?
        transmission time = size/2e9
        propagation time = length/speed = 5e7/2e8 = 0.25 sec
        '''
        return self.filesize/2e9 + 0.25

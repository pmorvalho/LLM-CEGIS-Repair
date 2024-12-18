#!/usr/bin/python
#Title			: program.py
#Usage			: python program.py -h
#Author			: pmorvalho
#Date			: May 21, 2024
#Description		: Program class.
#Notes			: 
#Python Version: 3.11.9
# (C) Copyright 2024 Pedro Orvalho.
#==============================================================================

from abc import ABC
from mentor.test_suite import TestSuite
        
class Program(ABC):
    def __init__(self, path: str, test_suite: TestSuite = None, ipa_description: str = None, path_2_correct_prog: str = None, verbose : bool = False):
        self.path = path
        self.code = "".join(open(self.path, "r+").readlines())
        self.path_2_correct_prog = path_2_correct_prog
        self.correct_code = "".join(open(self.path_2_correct_prog, "r+").readlines()) if path_2_correct_prog else None
        self.test_suite = test_suite
        self.ipa_description = "".join(open(ipa_description, "r+").readlines()) if ipa_description else None
        self.verbose = verbose
        
    def get_code(self):
        return self.code

    def get_correct_code(self):
        return self.correct_code

    def get_description(self):
        return self.ipa_description

    def get_test_suite(self):
        return self.test_suite

    def get_io_tests(self):
        return self.test_suite.get_io_tests()

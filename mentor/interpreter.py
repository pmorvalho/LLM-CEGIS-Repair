#!/usr/bin/python
#Title			: interpreter.py
#Usage			: python interpreter.py -h
#Author			: pmorvalho
#Date			: May 21, 2024
#Description		: Interpreter class
#Notes			: 
#Python Version: 3.11.9
# (C) Copyright 2024 Pedro Orvalho.
#==============================================================================

from abc import ABC
from mentor.test_suite import TestSuite
import os

class Interpreter(ABC):
    def __init__(self, test_suite: TestSuite, verbose: bool = False):
        self.test_suite = test_suite
        self.verbose = verbose

    def check_program(self, prog_path : str):
        for t in self.test_suite.get_tests():
            if self.verbose:
                print("Checking test:", t)
            if self.check_program_on_test(prog_path, t):
                continue
            else:
                return False, t
        return True, None
        
    def check_program_on_test(self, prog : str, test_id: int):
        lines = os.popen("./mentor/program_checker.sh {p} {t}".format(p=prog, t=test_id)).read()
        if "WRONG\n" in lines:
            return False
        return True

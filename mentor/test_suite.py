#!/usr/bin/python
#Title			: test_suite.py
#Usage			: python test_suite.py -h
#Author			: pmorvalho
#Date			: May 21, 2024
#Description		: Test suite class.
#Notes			: 
#Python Version: 3.11.9
# (C) Copyright 2024 Pedro Orvalho.
#==============================================================================

from abc import ABC
import glob

class TestSuite(ABC):
    def __init__(self, path: str, verbose: bool = False):
        self.path = path
        self.verbose = verbose
        self.in_tests = glob.glob('{p}/*.in'.format(p=path), recursive=True)
        self.inputs = self.get_values(self.in_tests)
        self.out_tests = glob.glob('{p}/*.out'.format(p=path), recursive=True)
        self.outputs = self.get_values(self.out_tests)
        if self.verbose:
            print("Input tests:", self.in_tests)
            print("Input values:", self.inputs)
            print()
            print("Output tests:", self.out_tests)
            print("Output values:", self.outputs)            

    def get_tests(self):
        return self.in_tests

    def get_values(self, tests):
        tests_values = dict()
        for t in tests:
            t_id = t.split("/")[-1].split(".")[0]
            tests_values[t_id] = open(t, "r+").readlines()

        return tests_values

    def get_counter_example(self, t: str):
        if t:
            t = t.split("/")[-1].split(".")[0] 
        try:
            inp = "".join(self.inputs[t])
            out = "".join(self.outputs[t])
            return f"#input:\n{inp}\n#output:\n{out}\n"
        except:
            return None

    def get_io_tests(self):
        r = ""        
        for k, i in self.inputs.items():
            inp = "".join(i)
            out = "".join(self.outputs[k])
            r += f"#input:\n{inp}\n#output:\n{out}\n"
        return r

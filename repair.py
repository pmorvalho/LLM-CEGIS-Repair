#!/usr/bin/python
#Title			: repair.py
#Usage			: python repair.py -h
#Author			: pmorvalho
#Date			: May 07, 2024
#Description		: LLM-based repair using BentoML servers
#Notes			: 
#Python Version: 3.8.5
# (C) Copyright 2024 Pedro Orvalho.
#==============================================================================

from abc import ABC
import argparse
from _bentoml_impl.client import AbstractClient
import bentoml
# import code_diff as cd # another option is diffsitter
import glob
import logging
import re
# import runhelper
from sys import argv
import sys

#
from mentor.test_suite import TestSuite
from mentor.program import Program
from mentor.interpreter import Interpreter
from mentor.fault_loc_agent import FaultLocAgent

logger = logging.getLogger('mentor.repair')

#llm_url = "http://localhost:2222"
llm_timeout = 300
prompt_version = 1
ports={"Llama3" : 2220, "CodeLlama" : 2221, "Phi3" : 2222, "CodeGemma" : 2223, "Gemma" : 2224, "Granite" : 2225}


class LLMBasedRepair(ABC):

    def __init__(self, llm_model: str, program: Program, bentoml_client: AbstractClient, correct_prog : Program = None, use_io_tests : bool = False, use_counterexample : bool = False, use_ipa_description : bool = False, fault_loc: FaultLocAgent = None):
        self.bentoml_client = bentoml_client
        self.llm_model = llm_model
        self.prog = program
        self.use_ipa_description = use_ipa_description
        self.io_tests = use_io_tests
        self.use_counterexample = use_counterexample
        self.correct_prog = correct_prog
        self.var_map = None     # TODO
        self.fault_loc = fault_loc
        self.client_id : int = self.bentoml_client.register()
        print("New Client ID:", self.client_id)
        self.num_tries = 0

    def disconnect(self) -> None:
        with bentoml.SyncHTTPClient(llm_url, timeout=600) as client:
            client.clear(self.client_id)
            
    def create_prompt(self) -> str:
        incorrect = self.prog.get_code()
        # prompt = f"Query #{self.num_tries}:\nFix the following incorrect program. Provide me code only, no sentences, and no explanations. CODE ONLY. No Explanation!\n"
        if not self.fault_loc:
            prompt = f"Fix all semantic bugs in the buggy program below. Modify the code as little as possible. Do not provide any explanation.\n\n"
        elif not self.fault_loc.providing_sketches():
            prompt = f"Fix all buggy lines with '/* FIXME */' comments in the buggy program below. Modify the code as little as possible. Do not provide any explanation.\n\n"
        else:
            prompt = f"Complete all the '@ HOLES N @' in the incomplete program below. Modify the code as little as possible. Do not provide any explanation.\n\n"
        if self.use_ipa_description:
            descr = self.prog.get_description()
            # prompt += f"Exercise description:\n{descr}\n"
            prompt += f"### Problem Description ###\n{descr}\n"            
        if self.io_tests:
            io_tests = self.prog.get_io_tests()
            # prompt += f"Input-Output tests used:\n{io_tests}\n"
            prompt += f"### Test Suite\n{io_tests}\n"                                    
        if self.fault_loc == None:
            prompt += f"### Buggy Program <c> ###\n```c\n{incorrect}\n```\n\n"        
        else:
            incorrect = self.fault_loc.get_program_sketch()
            if incorrect != None and self.fault_loc.providing_sketches():
                prompt += f"### Incomplete Program <c> ###\n```c\n{incorrect}\n```\n\n"                
                # prompt += f"### Buggy Statemets ###\n```c\n{fl}\n```\n"            
            elif incorrect != None:
                prompt += f"### Buggy Program <c> ###\n```c\n{incorrect}\n```\n\n"
            else:
                self.fault_loc = None
                
        if self.correct_prog:
            correct = self.correct_prog.get_code()            
            # prompt += f"Consider the following correct implementation for the same exercise:\n\n{correct}\n"
            prompt += f"# Reference Implementation (Do not copy this program) <c> #\n```c\n{correct}\n```\n\n"
        
        if not self.fault_loc or (self.fault_loc and not self.fault_loc.providing_sketches()):
            prompt += "### Fixed Program <c> ###\n"
            if self.llm_model == "Granite" or self.llm_model == "CodeLlama":
                prompt += "```c\n"
        elif self.fault_loc and self.fault_loc.providing_sketches():
            prompt += "### Complete Program <c> ###\n"
            
        return prompt

    def create_response(self, counterexample: str = None) -> str:
        prompt = f"### Feedback ###\n Your previous suggestion was incorrect! Try again. CODE ONLY. Provide no explanation.\n\n"
        if self.use_counterexample:
            ce = self.prog.test_suite.get_counterexample(counterexample)
            # prompt += f"Counterexample:\n{ce}\n"                                    
            prompt += f"### Counterexample  ###\n{ce}\n"                        
        if self.fault_loc and (self.num_tries % 2) == 0:
            incorrect = self.fault_loc.get_program_sketch()
            if incorrect != None and self.fault_loc.providing_sketches():
                prompt += f"### Incomplete Program <c> ###\n```c\n{incorrect}\n```\n\n"
                # prompt += f"### Buggy Statemets ###\n```c\n{fl}\n```\n"
                
            elif incorrect != None:
                prompt += f"### Buggy Program <c> ###\n```c\n{incorrect}\n```\n\n"
            else:
                self.fault_loc = None
        if not self.fault_loc or (self.fault_loc and not self.fault_loc.providing_sketches()):
            prompt += "### Fixed Program <c> ###\n"
        return prompt    

    def parse_response(self, response: str) -> str:
        return response

    def repair(self, counterexample: str = None) -> str:        
        with bentoml.SyncHTTPClient(llm_url, timeout=600) as client:
            prompt = self.create_prompt() if self.num_tries == 0 else self.create_response(counterexample)
            print(f"#Attempt={self.num_tries}")
            print("\nPrompt:\n")
            print(prompt)
            result = client.repair(self.client_id, prompt)
            print(result)
            print()
            print()
            # Regular expression to match content inside triple backticks
            if "### Fixed Program <c> ###" in result:
                result = result.split("### Fixed Program <c> ###")[1]
            result = result.split("\n")
            if "```c" in result:
                b = result.index("```c")
                result = result[b+1:]
            else:
                for r in range(len(result)):
                    if "  Here is " in result[r]:
                        result = result[r+2:]
                        break
            if "```" in result:
                e = result.index("```")
                result = result[:e]
            for i in range(len(result)):
                if len(result[i]) > 0 and "#include" in result[i]:
                    result = result[i:]
                    break
            result = "\n".join(result)
            print(f"### LLM Program - {self.llm_model}  ###\n```c\n{result}\n```\n")                        
            self.num_tries += 1
            return result
        
class RepairAgent(ABC):

    def __init__(self, llm_model: str, program: Program, output_file: str, interpreter: Interpreter = None, correct_prog : Program = None, use_io_tests : bool = False, use_counterexample : bool = False, use_ipa_description : bool = False, fault_loc: FaultLocAgent = None, verbose: bool = False):
        self.llm_model = llm_model
        self.program = program
        self.interpreter = interpreter
        self.fault_loc = fault_loc
        self.repair_model = LLMBasedRepair(llm_model, program, bentoml.SyncHTTPClient(llm_url, timeout=600), correct_prog, use_io_tests, use_counterexample, use_ipa_description, fault_loc)
        self.output_file = output_file
        self.verbose = verbose

    def terminal_state(self, cprog):        
        logger.info('Program fixed!')
        print('Program fixed!\n')
        correct_lines = "".join(open(cprog, "r+").readlines()).split("\n")
        incorrect_lines = self.program.get_code().split("\n")
        diff = max(len([l for l in incorrect_lines if l not in correct_lines]), len([l for l in correct_lines if l not in incorrect_lines]))
        print("#AST Edits={e}".format(e=diff))
        if self.verbose:            
            print("#Attempts={a}\n".format(a=self.repair_model.num_tries))
        c = "\n".join(correct_lines)
        print(f"\n### Fixed Program - {self.llm_model}  ###\n```c\n{c}\n```\n")                                    
        self.repair_model.disconnect()
        sys.stdout.flush() 

    def check_fix(self, cprog):
        if self.interpreter is None:
            logger.error('Interpreter is missing')
            raise RuntimeError()
        try:
            result, ce = self.interpreter.check_program(cprog)
        except (RuntimeError):
            logger.warning('Failed to eval:\n', cprog)
            return False, None

        if result:
            self.terminal_state(cprog)
            return True, None

        return False, ce

    def repair(self):
        ce = None
        while True:
            r = self.repair_model.repair(ce)
            with open(self.output_file, 'w+') as writer:
                writer.write(r)
            fixed, ce = self.check_fix(self.output_file)
            if fixed:
                break
            sys.stdout.flush() 
        return

def parser():
    parser = argparse.ArgumentParser(prog='repair.py', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i', '--inc_prog', help='Program to be repaired.')
    parser.add_argument('-c', '--cor_prog', help='Correct program to serve as a reference implementation.')    
    parser.add_argument('--ipa_description', help='Path to the IPA\'s description, that will be provided to the LLM model.')
    parser.add_argument('--llm', type=str, default='Llama3', help='LLM Bento Server. LLM\'s name.')
    parser.add_argument('--server', type=str, default='draco', help='LLM Bento Server. LLM\'s name.')    
    parser.add_argument('-ce', '--counterexample', action='store_true', default=False, help='Gives the LLM model a counter example why its suggestion is incorrect.')
    parser.add_argument('-io', '--use_io_tests', action='store_true', default=False, help='Provides the IO test suite to the LLM model.')
    parser.add_argument('-e', '--ipa', help='Name of the lab and exercise (IPA) so we can check the IO tests.')
    parser.add_argument('-fd', '--faults_dict', nargs='?', default=None, help='Path to the dictionary where the faults are stored at.')
    parser.add_argument('-sk', '--sketches', action='store_true', default=False, help='Provides sketches of the incorrect programs without the buggy statements to the LLM model. The buggy statements are provided using --faults_dict.')
    parser.add_argument('-o', '--output_file', nargs='?', help='the name of the output file.')
    parser.add_argument('-td', '--test_dir', help='Test dir.')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='Prints debugging information.')
    args = parser.parse_args(argv[1:])
    return args

if __name__ == '__main__':
    args = parser()
    llm_url = "http://{s}:{p}".format(s=args.server, p=ports[args.llm])
    if args.verbose:
        print("Contacting {u}".format(u=llm_url))
    ts = TestSuite(args.test_dir, args.verbose)
    p = Program(args.inc_prog, ts, ipa_description = args.ipa_description, verbose = args.verbose)
    c = Program(args.cor_prog, ts, verbose = args.verbose) if args.cor_prog != None else None
    i = Interpreter(ts, args.verbose)
    fault_loc = FaultLocAgent(p, args.faults_dict, args.sketches, verbose = args.verbose) if args.faults_dict != None else None
    ra = RepairAgent(args.llm, p, args.output_file, i, correct_prog=c, use_io_tests=args.use_io_tests, use_counterexample=args.counterexample, use_ipa_description = True if args.ipa_description != None else False, fault_loc=fault_loc, verbose=args.verbose)
    ra.repair()

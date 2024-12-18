#!/usr/bin/python
#Title			: fault_loc_agent.py
#Usage			: python fault_loc_agent.py -h
#Author			: pmorvalho
#Date			: June 28, 2024
#Description		: FaultLocAgent Class, creates holes in the incorrect program by introducing FIXME comments or by replacing the buggy lines with @ HOLES @.
#Notes			: 
#Python Version: 3.8.5
# (C) Copyright 2024 Pedro Orvalho.
#==============================================================================

from mentor.program import Program

from abc import ABC
import gzip
import pickle

def load_dict(d):
    fp=gzip.open(d,'rb')
    d_map=pickle.load(fp)
    fp.close()
    return d_map

class FaultLocAgent(ABC):
    def __init__(self, program: Program, fault_dict: dict(), insert_holes: bool = False, verbose: bool = False):
        self.prog = program
        self.fault_dict = fault_dict
        if fault_dict != None: 
            self.fault_dict = load_dict(fault_dict)
            self.fault_dict = self.fault_dict[list(self.fault_dict.keys())[0]]
        self.insert_holes = insert_holes

    def providing_sketches(self):
        return self.insert_holes
        
    def get_fault_localization(self):
        if self.fault_dict != None and isinstance(self.fault_dict, list) and len(self.fault_dict) > 0:
            if "faults" in self.fault_dict[0].keys():
                f = self.fault_dict[0]["faults"]
                self.fault_dict.pop(0)
                return f
            else:
                self.fault_dict.pop(0)

    def get_program_sketch(self):
        faults = self.get_fault_localization()
        p = self.prog.get_code().split("\n")
        nh=1
        if faults != None:
            p = self.prog.get_code().split("\n")
            for _, l, _, _, _ in faults:
                if self.insert_holes:
                    p[l-1] = f"@ HOLE {nh} @"
                else:
                    p[l-1] += f" /* FIXME */"
                nh+=1
            return "\n".join(p)
        else:
            return None

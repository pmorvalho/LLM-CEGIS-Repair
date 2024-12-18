#!/usr/bin/python
#Title			: compute_ASTs_metrics.py
#Usage			: python compute_ASTs_metrics.py -h
#Author			: pmorvalho
#Date			: July 09, 2024
#Description		: Computes the Levenshtein Distance, Tree Edit Distance and the number of matching subtrees between two programs.
#Notes			: 
#Python Version: 3.11.9
# (C) Copyright 2024 Pedro Orvalho.
#==============================================================================

import argparse
from collections import defaultdict
import hashlib
import Levenshtein
from pycparser import c_parser, c_ast,  parse_file
from sys import argv
import zss

def get_AST(f):
    def visit_FileAST(node):
        #print('****************** Found FileAST Node with Parent Node ****************')
        n_ext = []
        fakestart_pos = -1 #for the case of our injected function which do not have the fakestart function in their ast
        for e in range(len(node.ext)):
            x = node.ext[e]
            # n_ext.append(self.visit(x, node_id(x.coord)))
            if isinstance(x, c_ast.Typedef) and isinstance(x.type, c_ast.TypeDecl) and "xcb_visualid_t" in x.type.declname:
                    fakestart_pos=e
                    break

        node.ext = node.ext[fakestart_pos+1:]
        return node
    
    ast1 = parse_file(f, use_cpp=True,
                      cpp_path='g++',
                      cpp_args=['-E', '-I../utils/fake_libc_include'])
    return visit_FileAST(ast1)    


def serialize_ast(node):
    result = []
    def recurse(node):
        if isinstance(node, c_ast.Node):
            result.append(node.__class__.__name__)
            for _, child in node.children():
                recurse(child)
    recurse(node)
    return result

def ast_to_zss(node):
    if isinstance(node, c_ast.Node):
        children = [ast_to_zss(child) for _, child in node.children()]
        return zss.Node(node.__class__.__name__, children)
    return zss.Node(str(node))

def hash_tree(node):
    """
    Generate a hash for the subtree rooted at `node`.
    """
    if not isinstance(node, c_ast.Node):
        return hashlib.md5(str(node).encode()).hexdigest()
    
    child_hashes = sorted(hash_tree(child) for _, child in node.children())
    combined = node.__class__.__name__ + ''.join(child_hashes)
    return hashlib.md5(combined.encode()).hexdigest()

def count_subtrees(node):
    """
    Count the occurrence of each subtree hash in the AST rooted at `node`.
    """
    subtree_count = defaultdict(int)
    
    def recurse(node):
        if isinstance(node, c_ast.Node):
            subtree_hash = hash_tree(node)
            subtree_count[subtree_hash] += 1
            for _, child in node.children():
                recurse(child)
    
    recurse(node)
    return subtree_count

def count_matching_subtrees(subtree_count1, subtree_count2):
    """
    Count the number of matching subtrees between two subtree hash counts.
    """
    matching_count = 0
    for subtree_hash in subtree_count1:
        if subtree_hash in subtree_count2:
            matching_count += min(subtree_count1[subtree_hash], subtree_count2[subtree_hash])
    return matching_count

def parser():
    parser = argparse.ArgumentParser(prog='compute_ASTs_metrics.py', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-p1', '--prog1', help='Program fixed by the LLM model.')
    parser.add_argument('-p2', '--prog2', help='Correct program to serve as a reference implementation.')
    parser.add_argument('-o', '--output_file', nargs='?', help='the name of the output file.')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='Prints debugging information.')
    args = parser.parse_args(argv[1:])
    return args

if __name__ == '__main__':
    args = parser()

    ast1 = get_AST(args.prog1)
    if args.verbose:
        print("1st Program")
        ast1.show()

    ast2 = get_AST(args.prog2)
    if args.verbose:
        print("2nd Program")
        ast2.show()
        
    if args.verbose:
        print("Serialize ASTs")
    serialized_ast1 = serialize_ast(ast1)
    serialized_ast2 = serialize_ast(ast2)
    
    if args.verbose:
        print("Transform ASTs to zss format")
    zss_ast1 = ast_to_zss(ast1)
    zss_ast2 = ast_to_zss(ast2)
    
    if args.verbose:
        print("Compute Levenshtein distance:")
    serialized_ast1_str = ' '.join(serialized_ast1)
    serialized_ast2_str = ' '.join(serialized_ast2)
    levenshtein_distance = Levenshtein.distance(serialized_ast1_str, serialized_ast2_str)
    print("Levenshtein Distance:", levenshtein_distance)
    
    # Compute Tree Edit Distance
    ted_distance = zss.simple_distance(zss_ast1, zss_ast2)
    print("Tree Edit Distance:", ted_distance)

    # Count subtrees in both ASTs
    subtree_count1 = count_subtrees(ast1)
    subtree_count2 = count_subtrees(ast2)
    
    # Compute the number of matching subtrees
    matching_subtrees = count_matching_subtrees(subtree_count1, subtree_count2)
    print("Number of Matching Subtrees:", matching_subtrees)

#!/usr/bin/env bash
#Title			: program_checker.sh
#Usage			: bash program_checker.sh program.c path_to_test.in
#Author			: pmorvalho
#Date			: July 20, 2022
#Description	        : Checks if a program is consistent with a set of IO tests for a given lab and exercise 
#Notes			: Outputs WRONG\n (resp. CORRECT\n) dependeing on failing (resp. passing) the input test
# (C) Copyright 2022 Pedro Orvalho.
#==============================================================================

initial_dir=$(pwd)
prog_2_check=$1
test_name=$2
# dataset=$initial_dir"/C-Pack-IPAs"

prog_name=$(echo $prog_2_check | rev | cut -d '/' -f 1 | rev)
wdir="wdir_"$prog_name"_"$RANDOM

#echo $wdir
if [[ ! -d $wdir ]]; then
    mkdir -p $wdir
fi

cp $prog_2_check $wdir/$prog_name
cd $wdir

#gcc -O3 -ansi -Wall $prog_name -lm -o prog_2_check.out 2> war.txt
gcc $prog_name -o prog_2_check.out 2> war.txt

t=$(echo $test_name | sed -e "s/\.in//" | sed -e "s/\.out//")
t_id=$(echo $t | rev | cut -d '/' -f 1 | rev)
timeout 10 ./prog_2_check.out < $t".in" > "p-"$t_id".out"
d=$(diff -w -B "p-"$t_id".out" $t".out")
#d=$(diff "p-"$t_id".out" $t".out")
if [[ $d == "" ]];
then
    echo "CORRECT"
else
    echo "WRONG"
fi
cd $initial_dir
rm -rf $wdir

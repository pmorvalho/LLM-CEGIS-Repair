#!/usr/bin/env bash
#Title			: run_code_metrics.sh
#Usage			: bash run_code_metrics.sh -h
#Author			: pmorvalho
#Date			: July 10, 2024
#Description		: Runs all code metrics on the fixed program, comparing it against the reference implementation and the original incorrect program
#Notes			:
# (C) Copyright 2024 Pedro Orvalho.
#==============================================================================

methods=("Llama3" "CodeLlama" "Phi3" "Gemma" "CodeGemma" "Granite")
options_names=("IPA_Description" "IO_Tests" "Counter_Example" "Reference_Implementation" "All_Basic_Features" "Closest_Program_InvAASTs" "Closest_Program_AASTs" "Fault_Localization" "Sketches" "All_FL" "All_Sketches" "All_Basic_Features_Using_Closest_Program_AAST" "All_FL-No_Ref_Implementation" "All_Sketches-No_Ref_Implementation" "All_Basic_Features-No_Ref_Implementation" "All_FL-No_Ref_Implementation-No_Counter_Example" "All_Sketches-No_Ref_Implementation-No_Counter_Example" "All_Basic_Features-No_Ref_Implementation-No_Counter_Example" "All_Basic_Features_FL" "All_Basic_Features_Sketches")
	       # "All_FL-No_Ref_Implementation-No_Test_Suite" "All_Sketches-No_Ref_Implementation-No_Test_Suite")

# note: FL, Sketches, All_FL and ALL_Sketches use the correct implementation from Closest_Program_AASTs

results_dir="results"
dataset_dir="C-Pack-IPAs"
data_dir="C-Pack-IPAs/incorrect_submissions"
closest_progs_dir_invs="" # TODO find closest_programs based on Invariants
closest_progs_dir="" # TODO find closest_programs based on ASTs
labs=("lab02" "lab03" "lab04")
years=("year-1" "year-2" "year-3")

TIMEOUT=120
initial_dir=$(pwd)

process_instance(){
    if [[ ! -d $d ]];
    then
	mkdir -p $d
    fi
    if [[ $(grep "fixed!" $d/repair/out.o) ]];
    then
       aux_dir=$d"/code_metrics"
       if [[ -d $aux_dir ]];
       then
	   rm -rf $aux_dir
       fi
       mkdir -p $aux_dir
       # if [[ $option_name == "Reference_Implementation" || $option_name = "All_Basic_Features" ]];
       # then
       cprog=$dataset_dir/reference_implementations/$lab/$ex.c
       # fi
       if [[ $option_name == "Closest_Program_AASTs" || $option_name = "All_FL" || $option_name = "All_Sketches" ]];
       then
	   cprog=$(ls $closest_progs_dir/$lab/$ex/$stu_id/*.c | tail -1)
	   if [[ $cprog == "" ]];
	   then
	       cprog=$dataset_dir/reference_implementations/$lab/$ex.c
	   fi
       else if [[ $option_name == "Closest_Programm_InvAASTs" ]];
	    then
		cprog=$(ls $closest_progs_dir_invs/$lab/$ex/$stu_id/*.c | tail -1)
		if [[ $cprog == "" ]];
		then
		    cprog=$dataset_dir/reference_implementations/$lab/$ex.c
		fi
	    fi
       fi

       $HOME/runsolver/src/runsolver -o $aux_dir/ast_diff-incorrect-fixed.txt -w $aux_dir/watcher1.w -v $aux_dir/var1.v -d 60 -W $TIMEOUT --vsize-limit $MEMOUT --rss-swap-limit $MEMOUT python3 $initial_dir/code_metrics/compute_ASTs_metrics.py -p1 $instance".c" -p2 $d/$stu_id"_fixed.c"
       $HOME/runsolver/src/runsolver -o $aux_dir/ast_diff-original-original.txt -w $aux_dir/watcher1.w -v $aux_dir/var1.v -d 60 -W $TIMEOUT --vsize-limit $MEMOUT --rss-swap-limit $MEMOUT python3 $initial_dir/code_metrics/compute_ASTs_metrics.py -p1 $instance".c" -p2 $instance".c"
       if [[ $cprog != "" ]];
       then
	   $HOME/runsolver/src/runsolver -o $aux_dir/ast_diff-original-reference.txt -w $aux_dir/watcher1.w -v $aux_dir/var1.v -d 60 -W $TIMEOUT --vsize-limit $MEMOUT --rss-swap-limit $MEMOUT python3 $initial_dir/code_metrics/compute_ASTs_metrics.py -p1 $instance".c" -p2 $cprog
	   $HOME/runsolver/src/runsolver -o $aux_dir/ast_diff-fixed-reference.txt -w $aux_dir/watcher2.w -v $aux_dir/var2.v -d 60 -W $TIMEOUT --vsize-limit $MEMOUT --rss-swap-limit $MEMOUT python3 $initial_dir/code_metrics/compute_ASTs_metrics.py -p1 $d/$stu_id"_fixed.c" -p2 $cprog
       fi
       rm $aux_dir/*.o
       rm $aux_dir/*.w
    fi
}

VERBOSE=0
while [[ $# -gt 0 ]]
do
key="$1"
case $key in
    -l|--llm)
	    methods=("$2")
	    shift
	    shift
    ;;
    -v|--verbose)
	    VERBOSE=1
	    shift
    ;;
    -h|--help)
	echo "USAGE: $0 [-l|--llm]
    	Options:
	--> -l|--llm -- LLM Model's name.
	--> -v|--verbose -- Set level of verbosity
	--> -h|--help -- to print this message"
	exit
    shift
    ;;
    *)
	echo "run_code_metrics.sh: error: unrecognized arguments: $key"
	echo "Try [-h|--help] for help"
	shift
	exit
	;;

esac
done

if [[ ! -d $results_dir ]];
then
    mkdir -p $results_dir
fi

for((m=0;m<${#methods[@]};m++));
    do
	method=${methods[$m]}
	for((r=0;r<${#options_names[@]};r++));
	do
	    option_name=${options_names[$r]}
	    r_dir=$results_dir/$method/$option_name
	    if [[ ! -d $r_dir ]];
	    then
		continue
	    fi
	    for((y=0;y<${#years[@]};y++));
	    do
		year=${years[$y]}
		for((l=0;l<${#labs[@]};l++));
		do
		    lab=${labs[$l]}
		    for ex in $(find $dataset_dir/semantically_incorrect_submissions/$year/$lab/ex* -maxdepth 0 -type d);
		    do
			ex=$(echo $ex | rev | cut -d '/' -f 1 | rev)
			for instance in $(find $dataset_dir/semantically_incorrect_submissions/$year/$lab/$ex/* -maxdepth 0 -mindepth 0 -type d);
			do
			    stu_id=$(echo $instance | rev | cut -d '/' -f 1 | rev)
			    if [[ $VERBOSE == 1 ]];
			    then
				echo $r_dir/$year/$lab/$ex/$stu_id
			    fi
			    p_id=$year/$lab/$ex/$stu_id
			    d=$r_dir/$p_id
			    process_instance &
			done
			wait
		    done
		done
	    done
	    echo
	    echo
	    echo "$method: $option_name done"
	done
done

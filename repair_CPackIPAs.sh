#!/usr/bin/env bash
#Title			: repair_CPackIPAs.sh
#Usage			: bash repair_CPackIPAs.sh
#Author			: pmorvalho
#Date			: May 21, 2024
#Description		: Calls our LLM-based repair agent on the C-Pack-IPAs dataset
#Notes			:
# (C) Copyright 2024 Pedro Orvalho.
#==============================================================================

# options=("--ipa_description" "-io" "-ce" "-c" "--ipa_description -io -ce -c" "-c" "-fd" ALL)
options_names=("IPA_Description" "IO_Tests" "Counter_Example" "Reference_Implementation" "All_Basic_Features" "Closest_Program_InvAASTs" "Closest_Program_AASTs" "Fault_Localization" "Sketches" "All_FL" "All_Sketches" "All_Basic_Features_Using_Closest_Program_AAST" "All_FL-No_Ref_Implementation" "All_Sketches-No_Ref_Implementation" "All_Basic_Features-No_Ref_Implementation" "All_FL-No_Ref_Implementation-No_Counter_Example" "All_Sketches-No_Ref_Implementation-No_Counter_Example" "All_Basic_Features-No_Ref_Implementation-No_Counter_Example" "All_Basic_Features_FL" "All_Basic_Features_Sketches")
# options_names=("All_FL-No_Ref_Implementation-No_Test_Suite" "All_Sketches-No_Ref_Implementation-No_Test_Suite" "All_Basic_Features_FL-No_Counter_Example" "All_Basic_Features_Sketches-No_Counter_Example" "All_FL-No_Counter_Example" "All_Sketches-No_Counter_Example" "IPA_Description" "IO_Tests" "Counter_Example" "Closest_Program_AASTs" "Closest_Program_InvAASTs")
# Note: FL, Sketches, All_FL and ALL_Sketches use the correct implementation from Closest_Program_AASTs

results_dir="results"
dataset_dir="C-Pack-IPAs"
data_dir="C-Pack-IPAs/incorrect_submissions"
closest_progs_dir_invs="" # TODO find closest_programs based on Invariants
closest_progs_dir="" # TODO find closest_programs based on ASTs
faults_loc_dir="CFaults/C-Pack-IPAs/incorrect_submissions/"
labs=("lab02" "lab03" "lab04")
years=("year-1" "year-2" "year-3")

TIMEOUT=90
MEMOUT=10000

process_instance(){
    if [[ ! -d $d ]];
    then
	mkdir -p $d
    fi
    aux_dir=$d"/repair"
    if [[ ! -d $aux_dir ]];
    then
       mkdir -p $aux_dir
    fi
    flags=" --llm $LLM_SERVER --server $SERVER"
    if [[ $option_name == "All_Basic_Features_FL-No_Counter_Example" || $option_name == "All_Basic_Features_Sketches-No_Counter_Example" || $option_name == "All_FL-No_Ref_Implementation-No_Counter_Example" || $option_name ==  "All_Sketches-No_Ref_Implementation-No_Counter_Example" || $option_name ==  "All_Basic_Features-No_Ref_Implementation-No_Counter_Example" || $option_name == "All_FL-No_Ref_Implementation-No_Test_Suite" || $option_name == "All_Sketches-No_Ref_Implementation-No_Test_Suite" || $option_name ==  "All_Basic_Features-No_Ref_Implementation" || $option_name == "IPA_Description" || $option_name = "All_FL" || $option_name = "All_Sketches" || $option_name = "All_Basic_Features" || $option_name = "All_Basic_Features_Using_Closest_Program_AAST" || $option_name = "All_FL-No_Counter_Example" || $option_name = "All_Sketches-No_Counter_Example" || $option_name = "All_Basic_Features_FL" || $option_name = "All_Basic_Features_Sketches" || $option_name = "All_FL-No_Ref_Implementation" || $option_name = "All_Sketches-No_Ref_Implementation" ]];
    then
	flags=$flags" --ipa_description IPAs-descriptions/$lab/$ex.md "
    fi
    if [[ $option_name == "All_Basic_Features_FL-No_Counter_Example" || $option_name == "All_Basic_Features_Sketches-No_Counter_Example" || $option_name == "All_FL-No_Ref_Implementation-No_Counter_Example" || $option_name ==  "All_Sketches-No_Ref_Implementation-No_Counter_Example" || $option_name ==  "All_Basic_Features-No_Ref_Implementation-No_Counter_Example" || $option_name ==  "All_Basic_Features-No_Ref_Implementation" || $option_name == "IO_Tests" || $option_name = "All_FL" || $option_name = "All_Sketches" || $option_name = "All_Basic_Features" || $option_name = "All_Basic_Features_Using_Closest_Program_AAST" || $option_name = "All_FL-No_Counter_Example" || $option_name = "All_Sketches-No_Counter_Example" || $option_name = "All_Basic_Features_FL" || $option_name = "All_Basic_Features_Sketches" || $option_name = "All_FL-No_Ref_Implementation" || $option_name = "All_Sketches-No_Ref_Implementation" ]];
    then
	flags=$flags" -io "
    fi
    if [[ $option_name ==  "All_Basic_Features-No_Ref_Implementation" || $option_name == "All_FL-No_Ref_Implementation-No_Test_Suite" || $option_name == "All_Sketches-No_Ref_Implementation-No_Test_Suite" || $option_name == "Counter_Example" || $option_name = "All_FL" || $option_name = "All_Sketches" || $option_name = "All_Basic_Features" || $option_name = "All_Basic_Features_Using_Closest_Program_AAST" || $option_name = "All_Basic_Features_FL" || $option_name = "All_Basic_Features_Sketches" || $option_name = "All_FL-No_Ref_Implementation" || $option_name = "All_Sketches-No_Ref_Implementation" ]];
    then
	flags=$flags" -ce "
    fi
    if [[ $option_name == "All_Basic_Features_FL-No_Counter_Example" || $option_name == "All_Basic_Features_Sketches-No_Counter_Example" || $option_name == "Reference_Implementation" || $option_name = "All_Basic_Features" || $option_name = "All_Basic_Features_FL" || $option_name = "All_Basic_Features_Sketches" ]];
    then
	flags=$flags" -c $dataset_dir/reference_implementations/$lab/$ex.c"
    fi
    if [[ $option_name == "Closest_Program_AASTs" || $option_name = "All_FL" || $option_name = "All_Sketches" || $option_name = "All_Basic_Features_Using_Closest_Program_AAST" || $option_name = "All_FL-No_Counter_Example" || $option_name = "All_Sketches-No_Counter_Example" ]];
    then
	cprog=$(ls $closest_progs_dir/$lab/$ex/$stu_id/*.c | tail -1)
	if [[ $cprog != "" ]];
	then
	    flags=$flags" -c $cprog "
	else
	    flags=$flags" -c $dataset_dir/reference_implementations/$lab/$ex.c"
	fi
    else if [[ $option_name == "Closest_Programm_InvAASTs" ]];
	 then
	     cprog=$(ls $closest_progs_dir_invs/$lab/$ex/$stu_id/*.c | tail -1)
	     if [[ $cprog != "" ]];
	     then
		 flags=$flags" -c $cprog "
	     else
		 flags=$flags" -c $dataset_dir/reference_implementations/$lab/$ex.c"
	     fi
	 fi
    fi

    if [[ $option_name == "All_Basic_Features_FL-No_Counter_Example" || $option_name == "All_Basic_Features_Sketches-No_Counter_Example" || $option_name == "All_FL-No_Ref_Implementation-No_Counter_Example" || $option_name ==  "All_Sketches-No_Ref_Implementation-No_Counter_Example" || $option_name == "All_FL-No_Ref_Implementation-No_Test_Suite" || $option_name == "All_Sketches-No_Ref_Implementation-No_Test_Suite" || $option_name == "Fault_Localization" || $option_name == "Sketches" || $option_name = "All_FL" || $option_name = "All_Sketches" || $option_name = "All_FL-No_Counter_Example" || $option_name = "All_Sketches-No_Counter_Example" || $option_name = "All_Basic_Features_FL" || $option_name = "All_Basic_Features_Sketches" || $option_name = "All_FL-No_Ref_Implementation" || $option_name = "All_Sketches-No_Ref_Implementation" ]];
    then
	fault_loc_dict=$(ls $faults_loc_dir/$year/$lab/$ex/$stu_id/loc*.pkl.gz | tail -1)
	if [[ $fault_loc_dict != "" ]];
	then
	    if [[ $option_name == "Fault_Localization" ||  $option_name == "All_FL-No_Ref_Implementation-No_Counter_Example"  || $option_name == "All_FL-No_Ref_Implementation-No_Test_Suite" || $option_name == "All_Basic_Features_FL-No_Counter_Example" || $option_name = "All_FL" || $option_name = "All_FL-No_Counter_Example" || $option_name = "All_Basic_Features_FL" || $option_name = "All_FL-No_Ref_Implementation" ]];
	    then
     		flags=$flags" -fd $fault_loc_dict "
	    else if [[ $option_name == "Sketches" || $option_name = "All_Sketches" || $option_name ==  "All_Sketches-No_Ref_Implementation-No_Counter_Example" || $option_name == "All_Basic_Features_Sketches-No_Counter_Example" ||  $option_name = "All_Sketches-No_Counter_Example" || $option_name == "All_Sketches-No_Ref_Implementation-No_Test_Suite" || $option_name = "All_Basic_Features_Sketches" || $option_name = "All_Sketches-No_Ref_Implementation" ]];
		 then
     		     flags=$flags" -fd $fault_loc_dict -sk "
		 fi
	    fi
	fi
    fi
    $HOME/runsolver/src/runsolver -o $aux_dir/out.o -w $aux_dir/watcher.w -v $aux_dir/var.v -d 80 -W $TIMEOUT --vsize-limit $MEMOUT --rss-swap-limit $MEMOUT python3 repair.py -i $instance".c" -o $d/$stu_id"_fixed.c" -td $dataset_dir/tests/$lab/$ex/ -v $flags # | tee $aux_dir/out.o
    if [[ $(grep "TIMEOUT=t" $aux_dir/var.v) ]];
    then
	echo "TIMEOUT:$year/$lab/$ex/$stu_id"
	n_timeouts=$((n_timeouts+1))
    else
	if [[ $(grep "fixed!" $aux_dir/out.o) ]];
	then
	   echo "FIXED:$year/$lab/$ex/$stu_id "$(grep "Attempts=" $aux_dir/out.o)" "$(grep "Edits=" $aux_dir/out.o)
	   n_fixed=$((n_fixed+1))
	else
	    echo "FAILED:$year/$lab/$ex/$stu_id"
	    n_failed=$((n_failed+1))
	fi
    fi
}

while [[ $# -gt 0 ]]
do
key="$1"
case $key in
    -s|--server)
	    SERVER=$2
	    shift
	    shift
    ;;
    -l|--llm)
	    LLM_SERVER=$2
	    shift
	    shift
    ;;
    -v|--verbose)
	    VERBOSE=1
	    shift
    ;;
    -h|--help)
	echo "USAGE: $0 [-l|--llm] [-s|--server]
    	Options:
	--> -l|--llm -- LLM Model's name.
	--> -s|--server -- Server name. E.g. draco.
	--> -v|--verbose -- Set level of verbosity
	--> -h|--help -- to print this message"
	exit
    shift
    ;;
    *)
	echo "repair_CPackIPAs.sh: error: unrecognized arguments: $key"
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

telegram-send "LLM-based Repair ($LLM_SERVER)"
for((r=0;r<${#options_names[@]};r++));
do
    # option=${options[$r]}
    option_name=${options_names[$r]}
    r_dir=$results_dir/$LLM_SERVER/$option_name
    n_timeouts=0
    n_fixed=0
    n_failed=0
    echo "Dealing with "$option_name
    for((y=0;y<${#years[@]};y++));
    do
	year=${years[$y]}
	echo "Year: $year"
	for((l=0;l<${#labs[@]};l++));
	do
	    lab=${labs[$l]}
	    for ex in $(find $dataset_dir/semantically_incorrect_submissions/$year/$lab/ex* -maxdepth 0 -type d);
	    do
		ex=$(echo $ex | rev | cut -d '/' -f 1 | rev)
		echo "$LLM_SERVER: $option_name Year: $year Lab: $lab Exercise: $ex"
		for instance in $(find $dataset_dir/semantically_incorrect_submissions/$year/$lab/$ex/* -maxdepth 0 -mindepth 0 -type d);
		do
		    stu_id=$(echo $instance | rev | cut -d '/' -f 1 | rev)
		    p_id=$year/$lab/$ex/$stu_id
		    d=$r_dir/$p_id
		    process_instance
		    # &
		done
		# wait
	    done
	done
    done
    echo
    echo
    echo
    echo "$LLM_SERVER: $option_name"
    telegram-send "$LLM_SERVER: $option_name"
    echo "Fixed: $n_fixed"
    telegram-send "Fixed: $n_fixed ("$(python3 -c "print(int("$n_fixed")/(int("$n_timeouts")+int("$n_failed")+int("$n_fixed")))")")"
    echo "Timeouts: $n_timeouts"
    telegram-send "Timeouts: $n_timeouts"
    echo "Failed: $n_failed"
    telegram-send "Failed: $n_failed"
    echo
done

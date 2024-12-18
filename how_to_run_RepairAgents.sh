#!/usr/bin/env bash
#Title			: how_to_run_RepairAgents.sh
#Usage			: bash how_to_run_RepairAgents.sh
#Author			: pmorvalho
#Date			: August 18, 2024
#Description		: Commands to run all the RepairAgents
#Notes			: 
# (C) Copyright 2024 Pedro Orvalho.
#==============================================================================

SERVER_NAME="localhost"
# activate conda environment
conda activate llms
# to create the conda environment use the requirements.txt file

# to run each RepairAgents in parallel run the following commands
mkdir logs
time ./repair_CPackIPAs.sh -l Llama3 -s $SERVER_NAME | tee -a logs/llama3.log &
time ./repair_CPackIPAs.sh -l CodeLlama -s $SERVER_NAME | tee -a logs/codellama.log &
time ./repair_CPackIPAs.sh -l Phi3 -s $SERVER_NAME | tee -a logs/phi3.log &
time ./repair_CPackIPAs.sh -l Gemma -s $SERVER_NAME | tee -a logs/gemma.log &
time ./repair_CPackIPAs.sh -l CodeGemma -s $SERVER_NAME | tee -a logs/codegemma.log &
time ./repair_CPackIPAs.sh -l Granite -s $SERVER_NAME | tee logs/granite.log &

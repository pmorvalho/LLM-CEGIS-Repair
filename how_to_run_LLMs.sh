#!/usr/bin/env bash
#Title			: how_to_run_LLMs.sh
#Usage			: bash how_to_run_LLMs.sh
#Author			: pmorvalho
#Date			: August 18, 2024
#Description		: Commands to launch all LLMs in different GPUs
#Notes			: 
# (C) Copyright 2024 Pedro Orvalho.
#==============================================================================

# activate conda environment
conda activate llms
# to create the conda environment use the requirements.txt file

# run each of the following commands in different GPUs
python3 -m bentoml serve llama3:Llama3 --port 2220 --timeout 600 &
python3 -m bentoml serve codellama:CodeLlama --port 2221 --timeout 600 &
python3 -m bentoml serve phi3:Phi3 --port 2222 --timeout 600 &
python3 -m bentoml serve codegemma:CodeGemma --port 2223 --timeout 600 &
python3 -m bentoml serve gemma:Gemma --port 2224 --timeout 600 &
python3 -m bentoml serve gemma:Granite --port 2225 --timeout 600 &

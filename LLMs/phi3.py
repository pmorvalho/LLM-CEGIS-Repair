#!/usr/bin/python
#Title			: phi3.py
#Usage			: python phi3.py -h
#Author			: pmorvalho
#Date			: May 07, 2024
#Description		: Phi3 Bento Server.
#Notes			: 
#Python Version: 3.11.9
# (C) Copyright 2024 Pedro Orvalho.
#==============================================================================

from dataclasses import dataclass
from typing import Optional

import bentoml
from argparse_dataclass import ArgumentParser

from transformers import pipeline

@dataclass
class BentoConfig:
    repair_model_name: Optional[str] = "microsoft/Phi-3-mini-128k-instruct"
    # "meta-llama/Phi3-7b-hf"
    # repair_model_name: Optional[str] = "Phi3-13b-Instruct-hf"
    # repair_model_name: Optional[str] = "phi3/Phi3-7b-hf"
    max_lines: int = 250
    repair_prompt_version: int = 1
    gpu_id: int = 6
    use_8bit: bool = True
    temperature: int = 0.6
    top_p: int = 0.9


parser = ArgumentParser(BentoConfig)
config, _ = parser.parse_known_args()

@bentoml.service()
class Phi3():
    def __init__(self) -> None:
        # from peft import AutoPeftModelForSequenceClassification, AutoPeftModelForCausalLM
        from transformers import AutoTokenizer, BitsAndBytesConfig
        import transformers
        import torch
        
        # bnb_config = BitsAndBytesConfig(load_in_8bit=config.use_8bit, torch_dtype=torch.bfloat16)
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=False,
        )
        repair_model_name = config.repair_model_name
        self.repair_model = transformers.pipeline(
            "text-generation",
            model="{m}".format(m=config.repair_model_name),               
            model_kwargs={
                # "torch_dtype": torch.bfloat16,
            #               "attn_implementation": "flash_attention_2",
                          "quantization_config": bnb_config},
            # max_new_tokens=config.max_lines,
            device_map={"": config.gpu_id},
            tokenizer=AutoTokenizer.from_pretrained("microsoft/Phi-3-mini-128k-instruct", trust_remote_code=True),
            trust_remote_code=True
        )
        self.generation_args = {
            "max_new_tokens": config.max_lines,
            "return_full_text": False,
            "temperature": config.temperature,
            "do_sample": False,
        } 
        # print(self.repair_model("Hey how are you doing today?"))
        self.listeners_ids = 0
        self.conversations = dict()
        
    @bentoml.api
    def register(self) -> int:
        self.listeners_ids += 1
        self.conversations[self.listeners_ids] = []
        return self.listeners_ids

    @bentoml.api
    def clear(self, listener_id: int) -> None:
        if listener_id in self.conversations.keys():
            self.conversations[listener_id] = []

    @bentoml.api
    def repair(self, user_id: int, new_prompt: str) -> str:
        result = None
        if user_id in self.conversations.keys():
            self.conversations[user_id].append({"role" : "user", "content": new_prompt})
            # prompt = self.repair_model.tokenizer.apply_chat_template(
            #     self.conversations[user_id], 
            #     tokenize=False, 
            #     add_generation_prompt=True
            # )
            # terminators = [
            #     self.repair_model.tokenizer.eos_token_id,
            #     self.repair_model.tokenizer.convert_tokens_to_ids("<|eot_id|>")
            # ]
            # outputs = self.repair_model(
            #     prompt,
            #     max_new_tokens=config.max_lines,
            #     eos_token_id=terminators,
            #     do_sample=True,
            #     temperature=config.temperature,
            #     top_p=config.top_p,
            #     )
            # result = outputs[0]["generated_text"][len(prompt):]
            output = self.repair_model(self.conversations[user_id], **self.generation_args)
            result = output[0]['generated_text']
            self.conversations[user_id].append({"role" : "assistant", "content": result})
            print()
            print("Result for User:", user_id)
            print(result)
        return result
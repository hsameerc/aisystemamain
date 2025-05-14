#!/bin/bash
export OPENAI_API_KEY=""

openai tools fine_tunes.prepare_data -f /temp/filename

openai api fine_tunes.create -t training.jsonl -m ada --suffix "system support model"

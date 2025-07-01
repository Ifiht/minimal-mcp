#!/bin/bash

llama-server -m ./Qwen3-14B/qwen3-14b-Q5_K_M.gguf -ngl 99 --ctx-size 4096 --jinja
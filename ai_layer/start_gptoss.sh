#!/bin/bash
# Host B Startup Script
# Usage: ./start_vllm.sh

MODEL_PATH="/home/juli/gptoss/gpt-oss-20b"
PORT=8000

echo "Starting vLLM server for model: $MODEL_PATH on port $PORT"

# Ensure vLLM is installed: pip install vllm
~/gptoss/ai-layer/venv/bin/python3 -u -m vllm.entrypoints.openai.api_server \
    --model $MODEL_PATH \
    --served-model-name supervisor-ai \
    --host 0.0.0.0 \
    --port $PORT \
    --tensor-parallel-size 2 \
    --max-model-len 8192

#!/bin/bash
# Generic script to start any Ollama model
# Usage: ./start_ollama.sh <model_name>

MODEL=$1

if [ -z "$MODEL" ]; then
    echo "[ERROR] No model name provided."
    exit 1
fi

echo "=== Starting $MODEL via Ollama ==="

# 1. Ensure Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "[INFO] Starting Ollama serve..."
    export OLLAMA_HOST=0.0.0.0
    ollama serve &
    sleep 5
fi

# 2. Pull Model (skip if exists, but pull ensures it)
echo "[INFO] Ensuring $MODEL is pulled..."
ollama pull $MODEL &

# Wait briefly for pull to initialize or complete if cached
sleep 2

# 3. Preload model into memory
echo "[INFO] Preloading $MODEL..."
curl -s http://localhost:11434/api/generate -d "{\"model\": \"$MODEL\", \"prompt\": \"\", \"keep_alive\": \"45m\"}" > /dev/null 2>&1

echo "[INFO] $MODEL should now be ready or loading on port 11434"

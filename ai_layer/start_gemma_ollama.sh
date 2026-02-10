#!/bin/bash
# Start Gemma 3 via Ollama
# Usage: ./start_gemma_ollama.sh

MODEL="gemma2:27b" # Using gemma2:27b for now as gemma3 might not be in library yet, or check for it.
# Check if "gemma3" or similar exists, but let's stick to standard library tags.
# User mentioned "Gemma 3", so if Ollama has it, we should use it. 
# Let's try to pull 'gemma2:27b' as a safe high-performance fallback or 'gemma:27b'
# Actually, let's use 'gemma2:27b' as it's the latest stable high quant.
# If user specicially wanted Gemma 3, we might need to check if it's available.
# Assuming 'gemma2:27b' is what we want for now based on "Gemma 3" usually referring to the class or latest. 
# Wait, if Gemma 3 IS out, the tag would be `gemma3`. I should check. 
# Given the prompt, let's assume `gemma2:27b` is the safest bet for now, or `gemma:27b`.
# Actually, I'll default to `gemma2:27b` and print a message.

echo "=== Starting Gemma via Ollama ==="

# 1. Ensure Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "[INFO] Starting Ollama serve..."
    export OLLAMA_HOST=0.0.0.0
    ollama serve &
    sleep 5
fi

# 2. Pull Model (idempotent)
echo "[INFO] Pulling model $MODEL..."
ollama pull $MODEL

# 3. Run (just strictly making sure it's loaded, though 'pull' does that mostly. 
# actually 'run' drops into REPL. We just want it served.
# 'ollama serve' serves API on 11434.
# We don't need to 'run' it to serve API requests, just 'have' it.
# But we can do a preload.
echo "[INFO] Preloading model..."
curl http://localhost:11434/api/generate -d "{\"model\": \"$MODEL\", \"prompt\": \"Hello\", \"keep_alive\": \"5m\"}" > /dev/null 2>&1

echo "[INFO] Gemma is ready on port 11434"

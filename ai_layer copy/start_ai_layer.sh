#!/bin/bash
set -e

echo "=== SUPERVISOR AI: AI LAYER LAUNCHER ==="
# This script deploys the full AI Layer (Ollama + Manager)
# It is designed to be run as a standard user (no sudo required).

# --- 0. Global Cleanup ---
export PATH=$PATH:/usr/local/bin:/usr/bin:$HOME/bin:$HOME/.local/bin:/snap/bin

echo "[1/8] Cleaning up existing AI processes..."
# Kill any existing manager, ollama, or vllm processes owned by this user
pkill -u $USER -f manager.py || true
pkill -u $USER -f "ollama serve" || true
pkill -u $USER -f "vllm.entrypoints.openai.api_server" || true
sleep 2

# ... (rest of the file remains similar until the end) ...

# We need to replace the whole content from line 6 to 83 or targeted replacement?
# I will use targeted checks.
# Wait, let's just replace the PATH line and the end.
# I'll do two chunks or use multi_replace.

# Kill any existing manager, ollama, or vllm processes owned by this user
pkill -u $USER -f manager.py || true
pkill -u $USER -f "ollama serve" || true
pkill -u $USER -f "vllm.entrypoints.openai.api_server" || true
sleep 2

# --- 1. Ollama Setup ---
echo "[2/8] Checking port 11434..."
# Check if port 11434 is still in use (possibly by system service or other user)
if lsof -i:11434 -t >/dev/null 2>&1; then
    echo "WARNING: Port 11434 is still in use."
    PID=$(lsof -t -i:11434)
    echo "Process $PID is holding port 11434."
    
    # Try to see if we can kill it (if it's ours but pkill missed it, or if we have rights)
    if kill -0 $PID 2>/dev/null; then
         echo "Attempting to kill PID $PID..."
         kill -9 $PID || echo "Failed to kill PID $PID. Ensure no system ollama is running."
    else
         echo "Cannot control PID $PID. Please stop the competing service manually (e.g., sudo systemctl stop ollama)."
         echo "Proceeding anyway, but 'ollama serve' may fail to bind."
    fi
else
    echo "Port 11434 is free."
fi

echo "[3/8] Configuring OLLAMA_HOST=0.0.0.0..."
export OLLAMA_HOST=0.0.0.0

echo "[4/8] Starting Ollama..."
# Start Ollama, pipe output to log and stdout
ollama serve 2>&1 | tee ollama.log &
OLLAMA_PID=$!
echo "Ollama started with PID $OLLAMA_PID"

echo "[5/8] Waiting for Ollama Readiness..."
# Infinite loop until it's up, user can Ctrl+C if they want
while true; do
    if curl -s http://localhost:11434/api/tags >/dev/null; then
        echo "Ollama is UP!"
        break
    fi
    echo "Waiting for Ollama..."
    sleep 2
done

# --- 2. Model Prep ---
MODEL="gemma2:27b"
echo "[6/8] Ensuring model '$MODEL' is pulled..."
# Check for ollama binary again
if command -v ollama >/dev/null 2>&1; then
    ollama pull $MODEL 2>&1 | tee -a ollama.log
else
    echo "ERROR: 'ollama' command not found. Model pull skipped."
fi

# --- 3. Manager Setup ---
echo "[7/8] Launching AI Manager..."
# Cleanup old manager
pkill -f manager.py || true

# Start Manager, pipe to tee
./venv/bin/python3 -u manager.py 2>&1 | tee manager.log &
MANAGER_PID=$!

echo "[8/8] Verifying Manager..."
sleep 2
if ps -p $MANAGER_PID > /dev/null; then
   echo "Manager is running with PID $MANAGER_PID"
else
   echo "ERROR: Manager failed to start. Check manager.log."
   exit 1
fi

echo "=============================================="
echo "AI LAYER DEPLOYED SUCCESSFULLY!"
echo "Ollama PID: $OLLAMA_PID (Port 11434)"
echo "Manager PID: $MANAGER_PID (Port 5002)"
echo "=============================================="
echo ""
echo "Streaming logs from manager.log and ollama.log..."
echo "Press Ctrl+C to stop watching logs (services will continue running in background)."
echo "=============================================="
tail -f manager.log ollama.log

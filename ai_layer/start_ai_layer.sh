#!/bin/bash
set -e

echo "=== SUPERVISOR AI: AI LAYER LAUNCHER ==="
echo "Mode: IDLE (User must select model via Dashboard)"
# This script deploys ONLY the AI Manager.
# It is designed to be run as a standard user.

# --- 0. Global Cleanup ---
export PATH=$PATH:/usr/local/bin:/usr/bin:$HOME/bin:$HOME/.local/bin:/snap/bin

echo "[1/4] Cleaning up ALL AI processes..."
# Kill any existing manager, ollama, or vllm processes owned by this user
pkill -u $USER -f manager.py || true
pkill -u $USER -f "ollama serve" || true
pkill -u $USER -f "vllm.entrypoints.openai.api_server" || true
sleep 2

# Double check cleanup
if pgrep -f "vllm.entrypoints.openai.api_server" > /dev/null; then
    echo "WARNING: vLLM processes still running. Attempting force kill..."
    pkill -9 -f "vllm.entrypoints.openai.api_server"
fi

# --- 1. Manager Setup ---
echo "[2/4] Launching AI Manager..."

# Start Manager, pipe to tee for Dual-Stream Logging (Terminal + File)
# -u for unbuffered output is critical.
nohup /home/juli/gptoss/venv/bin/python3 -u manager.py 2>&1 | tee manager.log &
MANAGER_PID=$!

echo "[3/4] Verifying Manager..."
sleep 2
if ps -p $MANAGER_PID > /dev/null; then
   echo "Manager is running with PID $MANAGER_PID"
else
   echo "ERROR: Manager failed to start. Check manager.log."
   exit 1
fi

echo "=============================================="
echo "AI LAYER MANAGER DEPLOYED"
echo "Manager PID: $MANAGER_PID (Port 5002)"
echo "Status: IDLE (Waiting for model selection)"
echo "=============================================="
echo ""
echo "Streaming logs from manager.log..."
echo "Press Ctrl+C to stop watching logs (Manager will continue in background)."
echo "=============================================="
tail -f manager.log

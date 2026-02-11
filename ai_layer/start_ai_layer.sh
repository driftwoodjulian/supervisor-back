#!/bin/bash
set -e

echo "=== SUPERVISOR AI: AI LAYER LAUNCHER ==="
echo "Mode: IDLE (User must select model via Dashboard)"
# This script deploys ONLY the AI Manager.
# It is designed to be run as a standard user.

# --- 0. Global Cleanup ---
export PATH=$PATH:/usr/local/bin:/usr/bin:$HOME/bin:$HOME/.local/bin:/snap/bin

echo "[1/4] Cleaning up ALL AI processes..."
# Kill any existing manager, ollama, or vllm processes
# Using strict sudo kill as requested for robustness

# 1. Stop System Services
sudo systemctl stop ollama || true

# 2. Gather PIDs
PIDS=$(pgrep -f "manager.py|ollama|vllm") || true

if [ -n "$PIDS" ]; then
    echo "Found lingering processes: $PIDS"
    echo "Force killing..."
    sudo kill -9 $PIDS || true
else
    echo "No lingering processes found."
fi

# Double check cleanup
if pgrep -f "vllm.entrypoints.openai.api_server" > /dev/null; then
    echo "WARNING: vLLM processes still running even after sudo kill. check manually."
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

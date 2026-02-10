#!/bin/bash
set -e

echo "=== Automated Ollama Setup ==="

# 1. Stop System Service (if exists)
echo "[1/6] Stopping systemd service (if active)..."
sudo systemctl stop ollama || echo "Service stop failed or service not found (ignoring)"

# 2. Kill any lingering process on port 11434
echo "[2/6] Cleaning up port 11434..."
PID=$(sudo lsof -t -i:11434)
if [ -n "$PID" ]; then
    echo "Killing PID $PID..."
    sudo kill -9 $PID
else
    echo "Port 11434 is free."
fi

# 3. Export Host Binding
echo "[3/6] Configuring OLLAMA_HOST=0.0.0.0..."
export OLLAMA_HOST=0.0.0.0

# 4. Start Ollama in Background
echo "[4/6] Starting Ollama..."
nohup ollama serve > ollama.log 2>&1 &
OLLAMA_PID=$!
echo "Ollama started with PID $OLLAMA_PID"

# 5. Wait for Readiness
echo "[5/6] Waiting for Ollama to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags >/dev/null; then
        echo "Ollama is UP!"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 1
done

# 6. Pull Model
MODEL="gemma2:27b"
echo "[6/6] Pulling model: $MODEL (This may take a while)..."
ollama pull $MODEL

echo "=== Setup Complete! ==="
echo "Ollama is running on 0.0.0.0:11434 with $MODEL loaded."

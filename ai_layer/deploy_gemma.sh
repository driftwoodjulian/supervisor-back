#!/bin/bash
# Deploy Gemma 3 27B with 8-bit quantization on 2x GPUs
# Usage: ./deploy_gemma.sh

MODEL_ID="google/gemma-3-27b-it"
PORT=8000

echo "=== Preparing to deploy $MODEL_ID ==="

# 1. Install/Update Dependencies
echo "[INFO] Installing/Updating required packages (vllm, bitsandbytes, huggingface_hub)..."
pip install -U vllm bitsandbytes huggingface_hub

# 2. Check Authentication
# Check if logged in to HF (token required for Gemma models)
if ! python3 -c "import huggingface_hub; token=huggingface_hub.get_token(); exit(0 if token else 1)"; then
    echo "----------------------------------------------------------------"
    echo "[WARN] Hugging Face authentication required to download Gemma weights."
    echo "Please find your token at https://huggingface.co/settings/tokens"
    echo "Logging in now..."
    huggingface-cli login
else
    echo "[INFO] Hugging Face authentication detected."
fi

# 3. Pre-download Model Weights (Recommended over git clone)
# This ensures the model is fully downloaded to the HF cache before vLLM starts.
echo "----------------------------------------------------------------"
echo "[INFO] Downloading model weights for $MODEL_ID..."
huggingface-cli download $MODEL_ID --exclude "*.gguf" # Download standard weights, exclude GGUF if present to save space

# 4. Start Server
# --quantization bitsandbytes: Reduces memory usage to fit 27B model on 48GB VRAM (approx 27GB required)
# --tensor-parallel-size 2: Distributes across both RTX 3090 GPUs
# --trust-remote-code: Often required for newest architecture versions
echo "----------------------------------------------------------------"
echo "[INFO] Starting vLLM server..."
echo "       Model: $MODEL_ID"
echo "       Quantization: bitsandbytes (8-bit)"
echo "       TP Size: 2"
echo "----------------------------------------------------------------"

# Fix for 2x 3090s hanging on NCCL P2P/shm broadcast
export NCCL_P2P_DISABLE=1
export NCCL_IB_DISABLE=1
# Fix for fragmentation on consumer GPUs
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

python3 -m vllm.entrypoints.openai.api_server \
    --model $MODEL_ID \
    --served-model-name supervisor-ai \
    --host 0.0.0.0 \
    --port $PORT \
    --tensor-parallel-size 2 \
    --max-model-len 4096 \
    --gpu-memory-utilization 0.90 \
    --quantization bitsandbytes \
    --load-format bitsandbytes \
    --trust-remote-code

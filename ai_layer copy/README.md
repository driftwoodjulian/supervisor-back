# AI Layer Deployment (Host B)

This directory contains the configuration for the AI Inference Host (Host B).

## Prerequisites
- Python 3.10+
- 3x CUDA-compatible GPUs (for Tensor Parallelism)
- `vllm` installed (`pip install vllm`)
- Model weights located at `/home/juli/gptoss/gpt-oss-20b`

## Deployment
1.  Copy `start_vllm.sh` to Host B.
2.  Make it executable: `chmod +x start_vllm.sh`
3.  Run the script: `./start_vllm.sh`
    - You can also wrap this in a systemd service for persistence.

## Configuration
The server runs on port 8000 by default and serves the model as `supervisor-ai`.

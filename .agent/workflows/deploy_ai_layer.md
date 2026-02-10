---
description: How to deploy and start the AI Layer on the remote server
---

# Deploy AI Layer

This workflow allows you to deploy the refactored AI Layer to the remote server (`10.10.1.8`) and start the Manager.

## Prerequisites
- SSH access to `juli@10.10.1.8`.
- Local checkout of the `supervisor-ai` repository.

## Steps

1. **Transfer Files**
   Copy the `ai_layer` directory to the remote server.
   ```bash
   scp -r ai_layer/manager.py ai_layer/start_ai_layer.sh ai_layer/tests juli@10.10.1.8:/home/juli/gptoss/ai-layer/
   ```

2. **Connect to Remote Server**
   ```bash
   ssh juli@10.10.1.8
   ```

3. **Navigate to AI Layer Directory**
   ```bash
   cd /home/juli/gptoss/ai-layer
   ```

4. **Start the AI Layer**
   Run the unified startup script. This will clean up old processes and start the Manager in IDLE mode.
   ```bash
   // turbo
   chmod +x start_ai_layer.sh
   nohup ./start_ai_layer.sh > /dev/null 2>&1 &
   ```

5. **Verify Deployment**
   Check that the Manager is running and listening.
   ```bash
   # Check process
   pgrep -a -f manager.py

   # Check logs
   tail -f manager.log
   ```

6. **(Optional) Run Verification Tests**
   If you want to verify the deployment integrity:
   ```bash
   /home/juli/gptoss/venv/bin/python3 tests/simulation_tests.py
   ```

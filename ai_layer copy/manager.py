import time
import subprocess
import os
import threading
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# State
current_state = {
    "model": "gptoss", # Default assumption, or check what's running
    "status": "unknown" # active, activating, turning_off, off
}

# Configuration
SCRIPTS = {
    "gptoss": "./start_gptoss.sh",
    "gemma": "./start_gemma_ollama.sh"
}
PORTS = {
    "gptoss": 8000,
    "gemma": 11434
}
PORT = 5002

def check_service_health(target_model):
    """Try to hit the health/models endpoint."""
    port = PORTS.get(target_model, 8000)
    url = f"http://127.0.0.1:{port}/v1/models"
    try:
        resp = requests.get(url, timeout=2)
        return resp.status_code == 200
    except:
        return False

def monitor_activation(target_model):
    """Background loop to check when vLLM is up."""
    print(f"[Manager] Monitoring activation of {target_model}...")
    current_state["status"] = "activating"
    
    # Wait up to 5 minutes
    for i in range(150):
        if check_service_health(target_model):
            print(f"[Manager] {target_model} is now ACTIVE on port {PORTS.get(target_model)}.")
            current_state["status"] = "active"
            current_state["model"] = target_model
            return
        time.sleep(2)
    
    print(f"[Manager] Timeout waiting for {target_model}.")
    current_state["status"] = "error_timeout"

def switch_logic(target_model):
    global current_state
    
    # 1. Turn Off
    print("[Manager] Stopping existing AI services...")
    current_state["status"] = "turning_off"
    
    # Kill vLLM (gptoss) always to free GPU
    subprocess.run(["pkill", "-f", "vllm.entrypoints.openai.api_server"])
    
    # Also kill Ollama to ensure VRAM is fully released for vLLM
    # We only really need to do this if switching TO gptoss, but doing it on any switch 
    # ensures a clean slate, effectively toggling between the two exclusive services.
    subprocess.run(["pkill", "ollama"])
    
    # Wait for processes to die
    time.sleep(5)
    
    # 2. Start New
    print(f"[Manager] Starting {target_model}...")
    current_state["status"] = "activating"
    current_state["model"] = target_model # Optimistic update
    
    script = SCRIPTS.get(target_model)
    if not script:
        current_state["status"] = "error_invalid_model"
        return

    # Start subprocess using manager's stdout/stderr
    # This ensures logs appear in the main manager.log (or terminal)
    subprocess.Popen(
        [script], 
        cwd=os.path.dirname(os.path.abspath(__file__)),
        stdout=None, # Inherit stdout
        stderr=None, # Inherit stderr
        preexec_fn=os.setsid 
    )
    
    # 3. Monitor
    threading.Thread(target=monitor_activation, args=(target_model,)).start()

@app.route('/switch', methods=['POST'])
def switch_model():
    data = request.json
    target = data.get("model")
    
    if target not in SCRIPTS:
        return jsonify({"error": "Invalid model"}), 400
        
    if current_state["status"] in ["activating", "turning_off"]:
        return jsonify({"error": "Busy switching"}), 409

    # Start switch in background thread to return immediately
    threading.Thread(target=switch_logic, args=(target,)).start()
    
    return jsonify({"message": f"Switching to {target} initiated", "status": "turning_off"})

@app.route('/status', methods=['GET'])
def get_status():
    # Periodic health check if we think we are active, to ensure truth
    if current_state["status"] == "active":
        if not check_service_health(current_state["model"]):
             current_state["status"] = "off" # It died?
             
    return jsonify(current_state)

if __name__ == '__main__':
    # Initial check
    # We need to guess what is running.
    if check_service_health("gptoss"):
         current_state["status"] = "active"
         current_state["model"] = "gptoss"
    elif check_service_health("gemma"):
         current_state["status"] = "active"
         current_state["model"] = "gemma"
    else:
        current_state["status"] = "off"

    app.run(host='0.0.0.0', port=PORT)

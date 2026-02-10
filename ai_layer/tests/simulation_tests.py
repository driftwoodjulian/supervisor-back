import requests
import time
import subprocess
import os
import sys

BASE_URL = "http://localhost:5002"

def test_early_bird():
    print("\n=== Simulation A: The 'Early Bird' ===")
    print("Action: Sending inference request immediately after idle boot.")
    try:
        # We assume manager is running (started by user or previous step)
        # But we need to ensure it's in IDLE state.
        # Let's hit the gatekeeper endpoint
        resp = requests.post(f"{BASE_URL}/v1/chat/completions", json={"messages":[]})
        
        if resp.status_code == 428:
            print("PASS: Backend rejected request with 428 Precondition Required.")
        else:
            print(f"FAIL: Expected 428, got {resp.status_code}. Resp: {resp.text}")
            return False
            
    except Exception as e:
        print(f"FAIL: Connection error or other exception: {e}")
        return False
    return True

def test_hot_toggle():
    print("\n=== Simulation B: The 'Hot Toggle' ===")
    print("Action: Start Model A, then switch to Model B after 10s.")
    
    # 1. Start Gemma (Model A)
    print("Requesting switch to 'gemma'...")
    requests.post(f"{BASE_URL}/switch", json={"model": "gemma"})
    
    print("Sleeping 10s...")
    time.sleep(10)
    
    # 2. Switch to GPTOSS (Model B)
    print("Requesting switch to 'gptoss'...")
    t0 = time.time()
    requests.post(f"{BASE_URL}/switch", json={"model": "gptoss"})
    
    # 3. Verify cleanup
    print("Verifying cleanup... (This runs concurrently with the manager's strict kill)")
    time.sleep(2) 
    
    # Check if 'ollama' is dying/dead. 
    # Note: Manager takes ~7s to kill (5s wait between TERM and KILL).
    # So at t+2s, it might still be there but TERM sent.
    # At t+10s, it MUST be gone.
    print("Waiting 10s for strict kill to finish...")
    time.sleep(10)
    
    # Check for Ollama processes
    res = subprocess.run(["pgrep", "ollama"], capture_output=True)
    if res.returncode == 0:
        print("FAIL: Ollama process still found! Strict kill failed.")
        return False
    else:
        print("PASS: Ollama process terminated.")
        
    print("PASS: Hot Switch sequence initiated without zombie processes.")
    return True

def test_marathon_boot():
    print("\n=== Simulation C: The 'Marathon Boot' ===")
    print("Action: Initiating switch to 'mock' model (simulating 35m boot).")
    
    # 1. Start Mock (Duration 5s for test, but logic supports long)
    # real test would need longer wait, but for verification we check it doesn't timeout immediately
    # and eventually succeeds.
    try:
        requests.post(f"{BASE_URL}/switch", json={"model": "mock"})
    except Exception as e:
        print(f"FAIL: Request failed: {e}")
        return False
        
    print("Waiting for mock boot (approx 10s+)...")
    time.sleep(15)
    
    # Check status
    try:
        resp = requests.get(f"{BASE_URL}/status").json()
        if resp["status"] == "active" and resp["model"] == "mock":
            print("PASS: Manager successfully waited and activated mock model.")
            return True
        else:
            print(f"FAIL: Manager status is {resp.get('status')}. Expected active.")
            return False
    except:
        return False

def test_log_audit():
    print("\n=== Simulation D: The 'Log Audit' ===")
    # Assumes running from ai_layer root or checks absolute path
    log_path = "/home/juli/gptoss/ai-layer/manager.log" 
    if not os.path.exists(log_path):
        print(f"FAIL: {log_path} not found (CWD: {os.getcwd()}).")
        return False
        
    print(f"PASS: Log file found at {log_path}.")
    return True

if __name__ == "__main__":
    print("Running Simulations...")
    
    # Ensure manager is reachable
    try:
        requests.get(f"{BASE_URL}/status")
    except:
        print("CRITICAL: Manager not running! Please start ./start_ai_layer.sh first.")
        sys.exit(1)

    fail = False
    if not test_early_bird(): fail = True
    if not test_hot_toggle(): fail = True
    if not test_marathon_boot(): fail = True
    if not test_log_audit(): fail = True
    
    if fail:
        print("\nSUMMARY: Some tests FAILED.")
        sys.exit(1)
    else:
        print("\nSUMMARY: All automated simulations PASSED.")

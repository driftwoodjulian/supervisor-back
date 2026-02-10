import requests
import json
import time
import random
import sys
import os

# Configuration
MANAGER_IP = "10.10.1.8"
MANAGER_URL = f"http://{MANAGER_IP}:5002"
BACKEND_URL = "http://127.0.0.1:5000" # Local backend to fetch chat data via existing API or DB access

def log(msg):
    print(f"[TEST] {msg}")

from backend.database import SourceSession
from backend.models import Chat, Message
from sqlalchemy import select, func

def get_random_chat():
    log("Fetching a random chat from Source DB...")
    session = SourceSession()
    try:
        # Get a random chat ID that has messages
        # Use func.random() for Postgres or random() for SQLite depending on source, 
        # but here we'll just pick latest 50 and choose one to be safe/fast.
        chats = session.execute(
            select(Chat).order_by(Chat.createdAt.desc()).limit(50)
        ).scalars().all()
        
        if not chats:
            log("No chats found in DB!")
            sys.exit(1)
            
        chat = random.choice(chats)
        log(f"Selected Chat ID: {chat.id}")
        
        # Fetch messages
        msgs = session.execute(
            select(Message).where(Message.chatId == chat.id).order_by(Message.createdAt)
        ).scalars().all()
        
        formatted_history = []
        for m in msgs:
            role = "user"
            # Simple heuristic for role if not explicit
            if m.author and isinstance(m.author, dict) and m.author.get("type") != "customer":
                 role = "agent"
            # Fallback based on text? No, assume user default if not agent.
            
            formatted_history.append({
                "role": role,
                "content": m.text or "",
                "timestamp": m.createdAt.isoformat() if m.createdAt else ""
            })
            
        return formatted_history
    except Exception as e:
        log(f"DB Error: {e}")
        sys.exit(1)
    finally:
        session.close()

def switch_model(model_name):
    log(f"Requesting switch to {model_name}...")
    try:
        resp = requests.post(f"{MANAGER_URL}/switch", json={"model": model_name})
        if resp.status_code not in [200, 409]: # 409 is busy, might be ok to wait
            log(f"Switch request failed: {resp.text}")
            sys.exit(1)
            
        # Poll for status
        log(f"Waiting for {model_name} to become ACTIVE...")
        start_time = time.time()
        while time.time() - start_time < 300: # 5 min timeout
            try:
                status_resp = requests.get(f"{MANAGER_URL}/status", timeout=2).json()
                if status_resp.get("status") == "active" and status_resp.get("model") == model_name:
                    log(f"SUCCESS: {model_name} is ACTIVE.")
                    return
            except:
                pass
            time.sleep(2)
            sys.stdout.write(".")
            sys.stdout.flush()
        
        log(f"\nTIMEOUT: {model_name} did not activate in time.")
        sys.exit(1)
    except Exception as e:
        log(f"Switch error: {e}")
        sys.exit(1)

def evaluate_chat(chat_history):
    # This mimics what ai_client.py does, but we do it manually here to verify the endpoint is reachable
    # We first need to know WHERE to send it.
    
    # 1. Ask Manager who is active
    status_resp = requests.get(f"{MANAGER_URL}/status").json()
    model = status_resp.get("model")
    
    if model == "gemma":
        ai_url = f"http://{MANAGER_IP}:11434/v1/chat/completions"
        ai_model = "gemma2:27b"
    else:
        ai_url = f"http://{MANAGER_IP}:8000/v1/chat/completions"
        ai_model = "supervisor-ai"
        
    log(f"Sending chat evaluation to {model} at {ai_url}...")
    
    payload = {
        "model": ai_model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Output JSON with a score."},
            {"role": "user", "content": json.dumps(chat_history)}
        ],
        "temperature": 0.1
    }
    
    try:
        resp = requests.post(ai_url, json=payload, timeout=300)
        resp.raise_for_status()
        log(f"Response Received: {resp.status_code}")
        # log(f"Body: {resp.text[:200]}...") # Truncate
        return True
    except Exception as e:
        log(f"Evaluation FAILED: {e}")
        return False

def main():
    log("=== STARTING END-TO-END VERIFICATION ===")
    
    chat = get_random_chat()
    
    # Test Gemma
    print("\n------------------------------------------------")
    switch_model("gemma")
    if evaluate_chat(chat):
        log("✅ GEMMA TEST PASSED")
    else:
        log("❌ GEMMA TEST FAILED")
        sys.exit(1)
        
    # Test GPT-OSS
    print("\n------------------------------------------------")
    switch_model("gptoss")
    if evaluate_chat(chat):
        log("✅ GPT-OSS TEST PASSED")
    else:
        log("❌ GPT-OSS TEST FAILED")
        sys.exit(1)
        
    print("\n================================================")
    log("🎉 ALL SYSTEMS GO: HYBRID ARCHITECTURE VERIFIED")
    print("================================================")

if __name__ == "__main__":
    main()

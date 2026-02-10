import requests
import json
from datetime import datetime, timedelta

# Configuration
# Configuration
# Based on satisfaction_sock.py, the AI service runs on 10.10.1.8
# HOST = "localhost" 
HOST = "10.10.1.8" 
PORT_BASE = 5040 # Ports are 5040, 5041, 5042

URL_SINGLE = f"http://{HOST}:{PORT_BASE}/ai/ai" 
URL_BATCH = f"http://{HOST}:{PORT_BASE}/ai/ai/batch_score"

def create_mock_conversation():
    now = datetime.now()
    t1 = (now - timedelta(minutes=10)).isoformat()
    t2 = (now - timedelta(minutes=9)).isoformat()
    t3 = (now - timedelta(minutes=5)).isoformat()
    t4 = (now - timedelta(minutes=2)).isoformat()

    return {
        "messages": [
            {"role": "client", "content": "Hola, tengo un problema", "timestamp": t1},
            {"role": "support agent", "content": "Hola, soy Jose. ¿En qué le ayudo?", "timestamp": t2, "author_name": "Jose"},
            {"role": "client", "content": "Quiero hablar con un supervisor", "timestamp": t3},
            {"role": "support agent", "content": "Hola, soy Maria, la supervisora.", "timestamp": t4, "author_name": "Maria"}
        ]
    }

def test_single_score():
    print(f"Testing Single Score at {URL_SINGLE}...")
    data = create_mock_conversation()
    try:
        response = requests.post(URL_SINGLE, json=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Response:", json.dumps(response.json(), indent=2))
        else:
            print("Error:", response.text)
    except Exception as e:
        print(f"Request failed: {e}")

def test_batch_score():
    print(f"\nTesting Batch Score at {URL_BATCH}...")
    # Batch expects a list of prompts
    data = [create_mock_conversation(), create_mock_conversation()]
    try:
        response = requests.post(URL_BATCH, json=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Response:", json.dumps(response.json(), indent=2))
        else:
            print("Error:", response.text)
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    print("WARNING: Ensure the AI service is running on port 5040.")
    test_single_score()
    test_batch_score()

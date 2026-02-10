import requests
import os
import sys

# Add project root to path to import env vars if needed, though we test via HTTP
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

GATEWAY_PORT = os.getenv('GATEWAY_PORT', '6000')
BASE_URL = f"http://127.0.0.1:{GATEWAY_PORT}/api"
LOGIN_URL = f"{BASE_URL}/login"
PROTECTED_URL = f"{BASE_URL}/evaluations"

def test_auth_flow():
    print(f"Testing Auth Flow via Gateway: {BASE_URL}")
    
    # 1. Attempt access without token
    print("\n1. Testing Unprotected Access (Should Fail)...")
    try:
        resp = requests.get(PROTECTED_URL)
        if resp.status_code == 401:
            print("SUCCESS: Access denied as expected.")
        else:
            print(f"FAILURE: Unexpected status code {resp.status_code}")
    except Exception as e:
        print(f"ERROR: {e}")

    # 2. Login
    print("\n2. Testing Login...")
    payload = {"username": "admin", "password": "admin"}
    try:
        resp = requests.post(LOGIN_URL, json=payload)
        if resp.status_code == 200:
            token = resp.json().get('token')
            if token:
                print("SUCCESS: Logged in and received token.")
            else:
                print("FAILURE: No token in response.")
                return
        else:
            print(f"FAILURE: Login failed with {resp.status_code}")
            return
    except Exception as e:
        print(f"ERROR: {e}")
        return

    # 3. Access with Token
    print("\n3. Testing Protected Access with Token...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(PROTECTED_URL, headers=headers)
        if resp.status_code == 200:
            print("SUCCESS: Accessed protected route.")
            data = resp.json()
            print(f"Received {len(data)} evaluations.")
        else:
            print(f"FAILURE: Access denied with valid token. Status: {resp.status_code}")
            print(resp.text)
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_auth_flow()

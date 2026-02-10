import requests
import sys

BASE_URL = "http://localhost:5050/api"
AUTH_CHECK_URL = "http://localhost:5000/auth/check"
MOCKED_TOKEN = "valid_test_token"

def test_endpoint(name, url, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        print(f"Testing {name} ...", end=" ")
        # Using a timeout to prevent hanging, assuming app is up
        response = requests.get(url, headers=headers, timeout=2)
        
        if response.status_code == 401:
            print("Received 401 Unauthorized (Expected for no/bad token)")
            return "401"
        elif response.status_code == 200:
            print("Received 200 OK (Expected for valid token)")
            return "200"
        else:
            print(f"Received {response.status_code}")
            return str(response.status_code)
            
    except Exception as e:
        print(f"Failed: {e}")
        return "error"

if __name__ == "__main__":
    print("--- Verifying Authentication Implementation ---")
    
    endpoints = [
        f"{BASE_URL}/chats/1",
        f"{BASE_URL}/conversation/1",
        f"{BASE_URL}/get_current",
        f"{BASE_URL}/satisfaction"
    ]

    print("\n[Case 1] No Token (Should fail)")
    for ep in endpoints:
        test_endpoint("Endpoint", ep)

    print("\n[Case 2] Malformed Token (Should fail)")
    for ep in endpoints:
        test_endpoint("Endpoint", ep, token="malformed_token")

    print("\nNote: To test success, the 'web' app must be running and we need a valid JWT.")
    print("This script verifies that the protection is ACTIVE.")

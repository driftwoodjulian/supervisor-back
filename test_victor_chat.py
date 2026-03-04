import requests
import jwt
import datetime

# Generate valid token
token = jwt.encode({
    'user': 'test_admin',
    'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
}, 'super_secret_key', algorithm="HS256")

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

data = {
    'message': 'hola',
    'history': []
}

print("Testing direct to backend (6001)...")
response = requests.post('http://127.0.0.1:6001/api/victor_chat', json=data, headers=headers)
print(f"Status 6001: {response.status_code}")
print(f"Body: {response.text}")

print("\nTesting via gateway (6002)...")
response2 = requests.post('http://127.0.0.1:6002/api/victor_chat', json=data, headers=headers)
print(f"Status 6002: {response2.status_code}")
print(f"Body: {response2.text}")

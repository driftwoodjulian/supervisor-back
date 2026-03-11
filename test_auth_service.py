import requests

try:
    url = "https://auth.towebs.com/api-token-auth/"
    data = {"username": "towebs", "password": "satancojealpapa"}
    resp = requests.post(url, data=data, timeout=10)
    print(f"Status from auth.towebs.com: {resp.status_code}")
    print(f"Body: {resp.text}")
except Exception as e:
    print(f"Error checking auth.towebs.com: {e}")

try:
    url2 = "https://nexus.towebs.com/api-token-auth/"
    resp2 = requests.post(url2, data=data, timeout=10)
    print(f"Status from nexus.towebs.com token gen: {resp2.status_code}")
    print(f"Body: {resp2.text}")
except Exception as e:
    print(f"Error checking nexus.towebs.com token: {e}")

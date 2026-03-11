import requests

url = "https://nexus.towebs.com/api-client-info/"
params = {"domain": "julianzeballos.com.ar"}
auth = ("towebs", "satancojealpapa")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}

print(f"Testing Basic Auth with Browser Spoofing against {url}")
try:
    response = requests.get(url, params=params, auth=auth, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

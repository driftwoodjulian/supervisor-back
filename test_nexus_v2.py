import requests

url = "https://nexus.towebs.com/api/v2/client/"
params = {"domain": "julianzeballos.com.ar"}
auth = ("towebs", "satancojealpapa")

print(f"Testing Basic Auth on {url} for {params['domain']}")
try:
    response = requests.get(url, params=params, auth=auth, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")

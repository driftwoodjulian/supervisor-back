import requests

domain = "julianzeballos.com.ar"
url = "https://nexus.towebs.com/api-client-info/"
params = {"domain": domain}

user = "towebs"
pwd = "satancojealpapa"

print(f"Testing basic auth against {url}")
response = requests.get(url, params=params, auth=(user, pwd), timeout=10)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

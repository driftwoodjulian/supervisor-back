import requests
import os
from dotenv import load_dotenv

load_dotenv('/home/julian/supervisor-ai/.env')

domain = "julianzeballos.com.ar"
url = f"https://nexus.towebs.com/api/v2/client/"
params = {"domain": domain}

user = os.getenv("NEXUS_BASIC_AUTH_USER")
pwd = os.getenv("NEXUS_BASIC_AUTH_PASS")

print(f"Testing basic auth with user: {user}")
response = requests.get(url, params=params, auth=(user, pwd), timeout=10)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

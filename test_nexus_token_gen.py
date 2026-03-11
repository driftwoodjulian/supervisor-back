import requests

url = "https://nexus.towebs.com/api-token-auth/"
data = {
    "username": "twnexus",
    "password": "satancojealpapa"
}

print(f"Testing Token Gen with user: {data['username']}")
response = requests.post(url, data=data, timeout=10)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

data["username"] = "towebs"
print(f"Testing Token Gen with user: {data['username']}")
response = requests.post(url, data=data, timeout=10)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

# And let's try the email address as user
data["username"] = "desarrollo@towebs.com"
print(f"Testing Token Gen with user: {data['username']}")
response = requests.post(url, data=data, timeout=10)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

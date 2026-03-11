import requests

try:
    auth_resp = requests.post(
        "https://auth.towebs.com/api-token-auth/",
        json={"username": "towebs", "password": "satancojealpapa"}
    )
    print("Auth Response:", auth_resp.status_code, auth_resp.text)
    
    if auth_resp.status_code == 200:
        token = auth_resp.json().get('token')
        nexus_resp = requests.get(
            "https://nexus.towebs.com/api/v2/client/",
            params={"domain": "plantascarnivoras.com"},
            headers={"Authorization": f"Token {token}"}
        )
        print("Nexus Response:", nexus_resp.status_code, nexus_resp.text)
        
except Exception as e:
    print("Error:", e)

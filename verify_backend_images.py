import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Admin token generation (hacky but works for local verification)
import jwt
import datetime

SECRET_KEY = "super_secret_key" # From api.py

def generate_token():
    token = jwt.encode({
        'user': 'test_admin',
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    }, SECRET_KEY, algorithm="HS256")
    return token

def verify_chat_images(chat_id):
    token = generate_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    url = f"http://localhost:5001/api/curation/chats?chat_id={chat_id}"
    print(f"Querying {url}...")
    
    try:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print(f"Error: {res.status_code} - {res.text}")
            return
            
        data = res.json()
        if not data:
            print("No data returned")
            return
            
        chat_data = data[0]
        raw_payload = chat_data.get('raw_payload')
        print(f"Raw Payload Preview (first 500 chars): {raw_payload[:500]}")
        
        if "[IMAGE_REF:" in raw_payload:
            print("SUCCESS: Found [IMAGE_REF:] tag in payload!")
            # Extract and print specific refs
            import re
            refs = re.findall(r'\[IMAGE_REF:\s*(.*?)\]', raw_payload)
            for ref in refs:
                print(f" - Found Image Ref: {ref}")
        else:
            print("FAILURE: No [IMAGE_REF:] tag found in payload.")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    verify_chat_images(18345)

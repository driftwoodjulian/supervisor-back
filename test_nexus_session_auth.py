import requests

session = requests.Session()
login_url = "https://nexus.towebs.com/garmin/login/"

try:
    print("1. Fetching login page to get csrftoken...")
    response = session.get(login_url, timeout=10)
    
    if 'csrftoken' not in session.cookies:
        print("Failed to get csrftoken cookie from GET request.")
    else:
        csrftoken = session.cookies['csrftoken']
        print(f"Got CSRF Token: {csrftoken}")
        
        login_data = {
            "csrfmiddlewaretoken": csrftoken,
            "username": "towebs",
            "password": "satancojealpapa",
            "next": "/garmin/" 
        }
        
        headers = {
            "Referer": login_url,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        }
        
        print("2. Attempting to log in...")
        post_response = session.post(login_url, data=login_data, headers=headers, timeout=10)
        print(f"Login POST Response status: {post_response.status_code}")
        
        if 'sessionid' in session.cookies:
            print("Successfully acquired sessionid cookie!")
        else:
            print("Login failed, no sessionid in cookies.")
            print(post_response.text[:200]) # Print snippet of failure
            
        print("3. Querying API client info with active Session...")
        api_url = "https://nexus.towebs.com/api-client-info/?domain=julianzeballos.com.ar"
        api_response = session.get(api_url, headers=headers, timeout=10)
        
        print(f"API Response Status Code: {api_response.status_code}")
        print(f"API Response JSON: {api_response.text}")

except Exception as e:
    print(f"Error during login or API call test: {e}")

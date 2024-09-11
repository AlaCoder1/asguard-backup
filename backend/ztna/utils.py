import requests
import json

def get_Zt_Token():
    url = "https://localhost:1280/edge/management/v1/authenticate?method=password"
    
    # Prepare the payload
    payload = {
        "username": "admin",
        "password": "admin"
    }
    
    # Convert the payload to JSON
    headers = {'Content-Type': 'application/json'}
    
    # Send the POST request
    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
    
    # Check if the request was successful
    if response.status_code == 200:
        response_json = response.json()
        token = response_json['data']['token']  
        return token
    else:
        print(f"Failed to authenticate. Status code: {response.status_code}")
        return None
    


from django.http import JsonResponse
import requests
import json


BASE_URL = "https://localhost:1280/edge/management/v1/"


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


def get_data(request, endpoint):
    url = BASE_URL + endpoint
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id}

    params = {
        "limit": 100,
    }

    response = requests.get(url, headers=headers, params=params,verify=False)

    if response.status_code == 200:
        data = response.json()
        corrected_data = json.dumps(data)
        return JsonResponse({"message": corrected_data}, status=201)
    return JsonResponse({"error": "Error in getting identites data"}, status=400)
    


import requests
import json

# Test successful login
try:
    login_data = {
        "email": "user1@example.com",
        "password": "password1"
    }
    response = requests.post('http://localhost:8000/api/v1/clients/login', data=json.dumps(login_data))
    print('Status:', response.status_code)
    if response.status_code == 200:
        data = response.json()
        print('Login successful:', data)
    else:
        print('Error:', response.text)
except Exception as e:
    print('Connection error:', e)

# Test unsuccessful login
try:
    login_data = {
        "email": "user1@example.com",
        "password": "wrongpassword"
    }
    response = requests.post('http://localhost:8000/api/v1/clients/login', data=json.dumps(login_data))
    print('Status:', response.status_code)
    if response.status_code == 401:
        data = response.json()
        print('Login failed as expected:', data)
    else:
        print('Error:', response.text)
except Exception as e:
    print('Connection error:', e)

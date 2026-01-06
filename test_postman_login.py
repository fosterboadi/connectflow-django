import requests
import json

url = "http://127.0.0.1:8000/api/v1/login/"
payload = {
    "email": "test@connectflow.com",
    "password": "Password123!"
}

response = requests.post(url, json=payload)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    data = response.json()
    print(f"\n✅ LOGIN SUCCESS!")
    print(f"Token: {data.get('token')}")
    print(f"User: {data.get('user', {}).get('email')}")
else:
    print(f"\n❌ LOGIN FAILED!")

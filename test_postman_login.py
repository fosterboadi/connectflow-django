import requests
import os

url = "http://127.0.0.1:8000/api/v1/login/"
payload = {
    "email": os.environ.get("TEST_LOGIN_EMAIL", ""),
    "password": os.environ.get("TEST_LOGIN_PASSWORD", ""),
}

if not all(payload.values()):
    raise SystemExit("Set TEST_LOGIN_EMAIL and TEST_LOGIN_PASSWORD to run this local diagnostic.")

response = requests.post(url, json=payload, timeout=10)
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"\n✅ LOGIN SUCCESS!")
    print(f"User: {data.get('user', {}).get('email')}")
else:
    error = response.json().get('error', 'Invalid credentials') if response.headers.get('content-type', '').startswith('application/json') else 'Unexpected response'
    print(f"\n❌ LOGIN FAILED: {error}")

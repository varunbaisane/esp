import urllib.request
import urllib.parse
import json

def test():
    # Login as admin
    login_data = urllib.parse.urlencode({
        "username": "admin@esp.local",
        "password": "password"
    }).encode("utf-8")
    
    req = urllib.request.Request("http://localhost:8000/api/v1/auth/login", data=login_data)
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read()
            token = json.loads(res_body).get("access_token")
    except Exception as e:
        print("Login failed:", e)
        return

    req2 = urllib.request.Request("http://localhost:8000/api/v1/team-operations")
    req2.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req2) as response2:
            print("Status code:", response2.status)
            print("Response:", response2.read().decode())
    except Exception as e:
        print("Request failed:", e)
        if hasattr(e, "read"):
            print("Response body:", e.read().decode())

test()

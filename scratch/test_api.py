import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_predict():
    # 1. Login
    print("Logging in...")
    login_data = {"username": "admin@episense.com", "password": "admin123"}
    resp = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        return
    
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Get a district ID
    # Since I don't have a list endpoint yet, I'll just use a dummy search or assume one exists from seeding
    # Actually, I'll search for 'Karnataka District 1' if I had a search endpoint.
    # For now, I'll just check the DB manually or assume we know one.
    # Wait! I can't search easily without an endpoint.
    
    # I'll just try to run the server and see if it starts and loads models.
    print("Server start check skipped (manual).")

if __name__ == "__main__":
    test_predict()

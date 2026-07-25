import os
import time
import httpx
import sys

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8001")

def test_backend():
    print("=== STARTING BACKEND INTEGRATION TESTS ===")
    
    # 1. Test User Signup
    email = f"test_{int(time.time())}@sme-test.com"
    password = "testpassword123"
    
    print(f"\n1. Testing Signup for {email}...")
    try:
        res = httpx.post(f"{BASE_URL}/auth/signup", json={"email": email, "password": password}, timeout=10)
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.json()}")
        if res.status_code != 200:
            print("Signup failed. Exiting.")
            return
    except Exception as e:
        print(f"Connection to backend failed: {e}")
        print("Please make sure the FastAPI backend is running! Run: python -m uvicorn backend.main:app --reload")
        return

    # 2. Test User Login
    print("\n2. Testing Login...")
    res = httpx.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    print(f"Status Code: {res.status_code}")
    auth_data = res.json()
    token = auth_data.get("access_token")
    if not token:
        print("Login failed, no token received.")
        return
    print(f"Token obtained: {token[:20]}...")
    
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Test File Ingestion (Upload)
    # We will upload the generated bank_statement.csv
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mock_data", "bank_statement.csv"))
    print(f"\n3. Testing Document Upload from {file_path}...")
    if not os.path.exists(file_path):
        print(f"Error: mock file does not exist at {file_path}. Please run python mock_data/generate_mock.py first.")
        return
        
    with open(file_path, "rb") as f:
        files = {"file": ("bank_statement.csv", f, "text/csv")}
        res = httpx.post(f"{BASE_URL}/documents/upload", headers=headers, files=files, timeout=10)
        
    print(f"Status Code: {res.status_code}")
    doc_data = res.json()
    doc_id = doc_data.get("id")
    print(f"Document Uploaded: {doc_data}")
    if not doc_id:
        print("Document upload failed.")
        return

    # 4. Test List Documents
    print("\n4. Testing List Documents...")
    res = httpx.get(f"{BASE_URL}/documents", headers=headers)
    print(f"Status Code: {res.status_code}")
    print(f"Documents in Inventory: {res.json()}")

    # 5. Run Autonomous Analysis Loop
    print("\n5. Triggering Autonomous Analysis (using API Key from environment if set)...")
    # You can pass a groq_api_key in the body if desired: {"doc_ids": [doc_id], "groq_api_key": "YOUR_KEY"}
    res = httpx.post(f"{BASE_URL}/analysis/run", headers=headers, json={"doc_ids": [doc_id]})
    print(f"Status Code: {res.status_code}")
    analysis_data = res.json()
    analysis_id = analysis_data.get("id")
    print(f"Analysis triggered successfully. ID: {analysis_id}")
    if not analysis_id:
        return

    # 6. Poll for step-by-step reasoning progress
    print("\n6. Polling Analysis status to watch agent reasoning progress...")
    while True:
        res = httpx.get(f"{BASE_URL}/analysis/{analysis_id}", headers=headers)
        data = res.json()
        status = data.get("status")
        progress = data.get("progress_message")
        print(f"[{status.upper()}] Progress: {progress}")
        
        if status in ["finished", "failed"]:
            print(f"\nFinal Status: {status.upper()}")
            if status == "finished":
                print("\n=== AGENT STRUCTURED OUTPUT ===")
                import json
                print(json.dumps(data.get("result"), indent=2))
            break
        time.sleep(1.5)

if __name__ == "__main__":
    test_backend()

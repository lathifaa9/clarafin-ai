import os
import time
import httpx

BASE_URL = "http://127.0.0.1:8000"

def test_clarafin_backend():
    print("=== STARTING CLARAFIN BACKEND INTEGRATION TESTS ===")
    
    # 1. Test Signup
    email = f"clarafin_test_{int(time.time())}@clarafin.com"
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
        print("Please make sure the Clarafin backend is running! Run: python -m uvicorn clarafin.backend.app.main:app --reload")
        return

    # 2. Test Login
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

    # 3. Test File Ingestion (Upload P&L and Bank Statement)
    # We will upload bank_statement.csv and profit_loss.xlsx from the sample_docs directory
    sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "sample_docs"))
    bank_path = os.path.join(sample_dir, "bank_statement.csv")
    pl_path = os.path.join(sample_dir, "profit_loss.xlsx")
    
    print(f"\n3. Testing Document Upload for bank statement and P&L...")
    doc_ids = []
    
    for path, filename, mime in [
        (bank_path, "bank_statement.csv", "text/csv"),
        (pl_path, "profit_loss.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    ]:
        if not os.path.exists(path):
            print(f"Error: mock file does not exist at {path}.")
            return
            
        with open(path, "rb") as f:
            files = {"file": (filename, f, mime)}
            res = httpx.post(f"{BASE_URL}/documents/upload", headers=headers, files=files, timeout=10)
            
        print(f"Uploaded {filename}: Status {res.status_code}")
        doc_data = res.json()
        doc_id = doc_data.get("id")
        if doc_id:
            doc_ids.append(doc_id)
            
    print(f"Uploaded Document IDs: {doc_ids}")
    if len(doc_ids) < 2:
        print("Failed to upload both test documents.")
        return

    # 4. Test List Documents
    print("\n4. Testing List Documents...")
    res = httpx.get(f"{BASE_URL}/documents", headers=headers)
    print(f"Status Code: {res.status_code}")
    print(f"Documents in Catalog: {len(res.json())} files found.")

    # 5. Trigger Autonomous Analysis Loop
    print("\n5. Triggering Autonomous Analysis on the uploaded documents...")
    res = httpx.post(f"{BASE_URL}/analysis/run", headers=headers, json={"doc_ids": doc_ids})
    print(f"Status Code: {res.status_code}")
    analysis_data = res.json()
    analysis_id = analysis_data.get("id")
    print(f"Analysis triggered successfully. ID: {analysis_id}")
    if not analysis_id:
        return

    # 6. Poll for progress tracking
    print("\n6. Polling Analysis status to watch live agent reasoning steps...")
    while True:
        res = httpx.get(f"{BASE_URL}/analysis/{analysis_id}", headers=headers)
        data = res.json()
        status = data.get("status")
        progress = data.get("progress_message")
        print(f"[{status.upper()}] Step: {progress}")
        
        if status in ["finished", "failed"]:
            print(f"\nFinal Status: {status.upper()}")
            if status == "finished":
                print("\n=== CLARAFIN AGENT STRUCTURED OUTPUT ===")
                import json
                print(json.dumps(data.get("result"), indent=2))
            break
        time.sleep(1.5)

if __name__ == "__main__":
    test_clarafin_backend()

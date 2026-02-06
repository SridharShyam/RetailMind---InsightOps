from fastapi.testclient import TestClient
from app.main import app
import sys

print("Initializing TestClient...")
try:
    client = TestClient(app)
    print("Sending request to /health...")
    response = client.get("/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    print("Sending request to /...")
    response = client.get("/")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")

except Exception as e:
    print(f"CRITICAL ERROR during TestClient run: {e}")
    import traceback
    traceback.print_exc()

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

print("Testing Simulator and Copilot Endpoints")
print("=" * 50)

# Test 1: Simulator - Price Change
print("\n[TEST 1] Simulator - Price Change")
try:
    resp = requests.post(
        f"{BASE_URL}/simulator/Pasta/price",
        json={"product_name": "Pasta", "new_price": 180.0}
    )
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print("SUCCESS - Simulator working!")
        print(json.dumps(resp.json(), indent=2))
    else:
        print(f"FAILED: {resp.text}")
except Exception as e:
    print(f"ERROR: {e}")

# Test 2: Copilot - Forecast Query
print("\n[TEST 2] Copilot - Forecast Query")
try:
    resp = requests.post(
        f"{BASE_URL}/copilot/query",
        json={"query": "What's the forecast for Coffee Beans?", "context": None}
    )
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print("SUCCESS - Copilot working!")
        data = resp.json()
        print(f"Intent: {data.get('intent')}")
        print(f"Response: {data.get('response')[:150]}...")
    else:
        print(f"FAILED: {resp.text}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 50)
print("Testing Complete!")

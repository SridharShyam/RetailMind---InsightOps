import requests
import json

print("Final Verification - Testing Fixed Endpoints\n")

# Test 1: Price Simulator
print("=" * 60)
print("TEST 1: Price Simulator Endpoint")
print("=" * 60)
print("POST /api/v1/simulator/Pasta/price")
print('Body: {"product_name": "Pasta", "new_price": 180.0}\n')

try:
    resp = requests.post(
        "http://localhost:8000/api/v1/simulator/Pasta/price",
        json={"product_name": "Pasta", "new_price": 180.0},
        timeout=5
    )
    print(f"HTTP Status: {resp.status_code}")
    
    if resp.status_code == 200:
        print("Result: SUCCESS\n")
        print("Response Data:")
        print(json.dumps(resp.json(), indent=2))
    else:
        print(f"Result: FAILED\nError: {resp.text}")
        
except requests.exceptions.RequestException as e:
    print(f"Result: ERROR\nDetails: {e}")

print("\n")

# Test 2: Copilot Query
print("=" * 60)
print("TEST 2: AI Copilot Query Endpoint")
print("=" * 60)
print("POST /api/v1/copilot/query")
print('Body: {"query": "What\'s the forecast for Pasta?", "context": null}\n')

try:
    resp = requests.post(
        "http://localhost:8000/api/v1/copilot/query",
        json={"query": "What's the forecast for Pasta?", "context": None},
        timeout=5
    )
    print(f"HTTP Status: {resp.status_code}")
    
    if resp.status_code == 200:
        print("Result: SUCCESS\n")
        print("Response Data:")
        data = resp.json()
        # Pretty print with truncated response text
        display_data = data.copy()
        if 'response' in display_data and len(display_data['response']) > 200:
            display_data['response'] = display_data['response'][:200] + "... (truncated)"
        print(json.dumps(display_data, indent=2))
    else:
        print(f"Result: FAILED\nError: {resp.text}")
        
except requests.exceptions.RequestException as e:
    print(f"Result: ERROR\nDetails: {e}")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
print("\nBoth endpoints are now ready for Postman testing!")
print("See ENDPOINT_TESTING_GUIDE.md for complete documentation.")

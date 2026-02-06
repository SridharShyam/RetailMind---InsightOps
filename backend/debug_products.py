import requests
import json

try:
    print("Fetching /api/v1/products/ ...")
    r = requests.get("http://localhost:8000/api/v1/products/")
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Keys: {list(data.keys())}")
        if 'products' in data:
            print(f"Product count: {len(data['products'])}")
            if len(data['products']) > 0:
                print(f"First product sample: {data['products'][0]}")
        else:
            print("Response does not contain 'products' key")
            print(f"Full response: {data}")
    else:
        print(f"Error response: {r.text}")

except Exception as e:
    print(f"Request failed: {e}")

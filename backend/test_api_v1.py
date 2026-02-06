
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def print_result(step, response):
    status = "✅ PASS" if response.status_code == 200 else "❌ FAIL"
    print(f"\n{step}: {status} ({response.status_code})")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    return response.status_code == 200

def test_api():
    print("🚀 Starting API Test Suite...")
    
    # 1. Health Check
    try:
        resp = requests.get("http://localhost:8000/health")
        if not print_result("Health Check", resp): return
    except Exception as e:
        print(f"❌ Server not reachable: {e}")
        return

    # 2. List Products
    resp = requests.get(f"{BASE_URL}/products/")
    if not print_result("List Products", resp): return
    
    products = resp.json().get('products', [])
    if not products:
        print("⚠️ No products found to test with.")
        return
    
    test_product = products[0]
    print(f"👉 Testing with product: {test_product}")
    
    # 3. Analyze Product
    resp = requests.get(f"{BASE_URL}/products/{test_product}/analyze")
    if not print_result(f"Analyze {test_product}", resp): return
    
    data = resp.json()
    initial_inventory = data.get('inventory_risk', {}).get('current_inventory', 0)
    print(f"   Initial Inventory: {initial_inventory}")
    
    # 4. Forecast
    resp = requests.get(f"{BASE_URL}/products/{test_product}/forecast")
    print_result("Get Forecast", resp)
    
    # 5. Pricing
    resp = requests.get(f"{BASE_URL}/products/{test_product}/pricing")
    print_result("Get Pricing", resp)
    
    # 6. Transaction (SALE)
    qty = 5
    payload = {
        "product_name": test_product,
        "quantity": qty,
        "transaction_type": "SALE"
    }
    resp = requests.post(f"{BASE_URL}/products/transaction", json=payload)
    if not print_result("Process Transaction (SALE)", resp): return
    
    print(f"   Response: {resp.json()}")
    
    # 7. Verify Inventory Update
    resp = requests.get(f"{BASE_URL}/products/{test_product}/analyze")
    if print_result("Verify Inventory Update", resp):
        new_inventory = resp.json().get('inventory_risk', {}).get('current_inventory', 0)
        print(f"   New Inventory: {new_inventory}")
        
        expected = max(0, initial_inventory - qty)
        if new_inventory == expected:
            print(f"✅ Inventory updated correctly: {initial_inventory} -> {new_inventory}")
        else:
            print(f"❌ Inventory mismatch! Expected {expected}, got {new_inventory}")

    # 8. Copilot Query
    payload = {
        "query": f"How is {test_product} performing?"
    }
    resp = requests.post(f"{BASE_URL}/copilot/query", json=payload)
    print_result("AI Copilot Query", resp)
    
    print("\n🏁 Test Suite Complete")

if __name__ == "__main__":
    test_api()

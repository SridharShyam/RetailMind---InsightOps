"""
Test script for Simulator and Copilot endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_simulator_endpoints():
    """Test simulator endpoints"""
    print("\n" + "="*60)
    print("🎯 TESTING SIMULATOR ENDPOINTS")
    print("="*60)
    
    # Test 1: Price Simulation
    print("\n1️⃣  Testing Price Simulation...")
    payload = {
        "product_name": "Pasta",
        "new_price": 180.0
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/simulator/Pasta/price", json=payload)
        print(f"   Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"   ✅ SUCCESS!")
            print(f"   Current Price: ₹{data.get('current_price', 0):.2f}")
            print(f"   New Price: ₹{data.get('new_price', 0):.2f}")
            print(f"   Price Change: {data.get('price_change_pct', 0):.1f}%")
            print(f"   Demand Impact: {data.get('demand_change_pct', 0):.1f}%")
            print(f"   Revenue Impact: {data.get('revenue_change_pct', 0):.1f}%")
            print(f"   Recommendation: {data.get('recommendation', 'N/A')}")
            print(f"\n   Full Response:")
            print(f"   {json.dumps(data, indent=2)}")
        else:
            print(f"   ❌ FAILED!")
            print(f"   Error: {resp.text}")
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")

def test_copilot_endpoints():
    """Test copilot endpoints"""
    print("\n" + "="*60)
    print("🤖 TESTING AI COPILOT ENDPOINTS")
    print("="*60)
    
    # Test 1: Forecast Query
    print("\n1️⃣  Testing Forecast Query...")
    payload = {
        "query": "What's the forecast for Coffee Beans?",
        "context": None
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/copilot/query", json=payload)
        print(f"   Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"   ✅ SUCCESS!")
            print(f"   Intent: {data.get('intent', 'N/A')}")
            print(f"   Response Preview: {data.get('response', '')[:200]}...")
            if 'data' in data and data['data']:
                print(f"   Data Keys: {list(data['data'].keys())}")
            print(f"\n   Full Response:")
            print(f"   {json.dumps(data, indent=2)}")
        else:
            print(f"   ❌ FAILED!")
            print(f"   Error: {resp.text}")
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
    
    # Test 2: Pricing Query
    print("\n2️⃣  Testing Pricing Query...")
    payload = {
        "query": "Should I change the price of Fresh Milk?",
        "context": None
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/copilot/query", json=payload)
        print(f"   Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"   ✅ SUCCESS!")
            print(f"   Intent: {data.get('intent', 'N/A')}")
            print(f"   Response Preview: {data.get('response', '')[:200]}...")
        else:
            print(f"   ❌ FAILED!")
            print(f"   Error: {resp.text}")
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
    
    # Test 3: Simulation Query via Copilot
    print("\n3️⃣  Testing Simulation Query via Copilot...")
    payload = {
        "query": "What if I reduce Pasta price by 10%?",
        "context": None
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/copilot/query", json=payload)
        print(f"   Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"   ✅ SUCCESS!")
            print(f"   Intent: {data.get('intent', 'N/A')}")
            print(f"   Response Preview: {data.get('response', '')[:200]}...")
        else:
            print(f"   ❌ FAILED!")
            print(f"   Error: {resp.text}")
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")

def main():
    """Run all tests"""
    print("\n🚀 STARTING ENDPOINT TESTS")
    print("Testing against:", BASE_URL)
    
    # Check health first
    try:
        resp = requests.get("http://localhost:8000/health")
        if resp.status_code == 200:
            print("✅ Server is healthy")
        else:
            print("⚠️  Server health check failed")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    test_simulator_endpoints()
    test_copilot_endpoints()
    
    print("\n" + "="*60)
    print("🏁 TESTS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()

"""
Test script to verify platform defaults work correctly.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Test 1: Create search with NO platforms selected (should default to ALL)
print("Test 1: Creating search with NO platforms selected...")
payload = {
    "product_name": "Test Product",
    "product_description": "Testing platform defaults",
    "budget": 100.0,
    "location": "Boston, MA",
    "match_threshold": 70.0,
    "search_craigslist": False,
    "search_ebay": False,
    "search_facebook": False
}

response = requests.post(f"{BASE_URL}/api/search-requests", json=payload)
print(f"Status: {response.status_code}")

if response.status_code == 201:
    data = response.json()
    print(f"✅ Search created: {data['id']}")
    print(f"   Craigslist: {data['search_craigslist']}")
    print(f"   eBay: {data['search_ebay']}")
    print(f"   Facebook: {data['search_facebook']}")
    
    # Expected: All should be True
    if data['search_craigslist'] and data['search_ebay'] and data['search_facebook']:
        print("✅ PASS: All platforms enabled as expected!")
    else:
        print("❌ FAIL: Not all platforms enabled")
else:
    print(f"❌ Error: {response.text}")

print("\n" + "="*60 + "\n")

# Test 2: Create search with ONLY Craigslist selected
print("Test 2: Creating search with ONLY Craigslist selected...")
payload2 = {
    "product_name": "Test Product 2",
    "product_description": "Testing single platform",
    "budget": 100.0,
    "location": "Boston, MA",
    "match_threshold": 70.0,
    "search_craigslist": True,
    "search_ebay": False,
    "search_facebook": False
}

response2 = requests.post(f"{BASE_URL}/api/search-requests", json=payload2)
print(f"Status: {response2.status_code}")

if response2.status_code == 201:
    data2 = response2.json()
    print(f"✅ Search created: {data2['id']}")
    print(f"   Craigslist: {data2['search_craigslist']}")
    print(f"   eBay: {data2['search_ebay']}")
    print(f"   Facebook: {data2['search_facebook']}")
    
    # Expected: Only Craigslist should be True
    if data2['search_craigslist'] and not data2['search_ebay'] and not data2['search_facebook']:
        print("✅ PASS: Only Craigslist enabled as expected!")
    else:
        print("❌ FAIL: Platform selection incorrect")
else:
    print(f"❌ Error: {response2.text}")

# Made with Bob

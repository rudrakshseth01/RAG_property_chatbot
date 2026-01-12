"""
Simple test script to verify the FastAPI application
Run this after starting the server to test all endpoints
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"


def test_root():
    """Test the root endpoint"""
    print("🔍 Testing Root Endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print("\n" + "="*50 + "\n")


def test_health():
    """Test the health check endpoint"""
    print("🔍 Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print("\n" + "="*50 + "\n")


def test_search():
    """Test the search endpoint"""
    print("🔍 Testing Property Search...")
    
    query_data = {
        "query": "3BHK apartment with lift and parking",
        "k_results": 5,
        "temperature": 0.2
    }
    
    response = requests.post(
        f"{BASE_URL}/search",
        json=query_data
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['total_results']} matching properties")
        print(f"\nExplanation: {data['explanation']}")
        
        if data['matching_projects']:
            print("\n🏢 Top matching properties:")
            for i, prop in enumerate(data['matching_projects'][:3], 1):
                print(f"\n{i}. {prop.get('projectName', 'N/A')}")
                print(f"   Location: {prop.get('location', 'N/A')}")
                print(f"   Price: {prop.get('price', 'N/A')}")
                print(f"   Type: {prop.get('type', 'N/A')}")
    else:
        print(f"Error: {response.text}")
    
    print("\n" + "="*50 + "\n")


def test_get_properties():
    """Test getting all properties"""
    print("🔍 Testing Get All Properties...")
    
    response = requests.get(
        f"{BASE_URL}/properties",
        params={"limit": 5, "offset": 0}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total properties: {data['total']}")
        print(f"Returned: {data['count']} properties")
        
        if data['properties']:
            print("\n🏢 First property:")
            prop = data['properties'][0]
            print(f"ID: {prop.get('unique_property_id', 'N/A')}")
            print(f"Price: {prop.get('price', 'N/A')}")
    else:
        print(f"Error: {response.text}")
    
    print("\n" + "="*50 + "\n")


def test_stats():
    """Test the statistics endpoint"""
    print("🔍 Testing Statistics...")
    
    response = requests.get(f"{BASE_URL}/stats")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total Properties: {data['total_properties']}")
        print(f"Average Price: ₹{data['average_price']:,.2f}")
        print(f"Price Range: ₹{data['min_price']:,} - ₹{data['max_price']:,}")
        
        print("\n📊 Property Types:")
        for ptype in data['property_types'][:5]:
            print(f"   {ptype['type']}: {ptype['count']}")
    else:
        print(f"Error: {response.text}")
    
    print("\n" + "="*50 + "\n")


def main():
    """Run all tests"""
    print("\n" + "="*50)
    print("🚀 Real Estate API - Test Suite")
    print("="*50 + "\n")
    
    try:
        test_root()
        test_health()
        test_stats()
        test_get_properties()
        test_search()
        
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API")
        print("Make sure the server is running: uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()

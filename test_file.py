"""
Quick test script to verify the test_transactions.csv file works correctly.
Run this after starting the server: python -m uvicorn main:app --reload
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"
FILENAME = "test_transactions.csv"

def test_get_transactions():
    """Test getting all transactions"""
    print("\n1. Testing: Get all transactions")
    response = requests.get(f"{BASE_URL}/transactions?filename={FILENAME}")
    if response.status_code == 200:
        data = response.json()
        print(f"   [OK] Success! Found {data['count']} transactions")
        print(f"   First transaction: {data['data'][0]['Description']}")
    else:
        print(f"   [ERROR] Error: {response.status_code} - {response.text}")

def test_search():
    """Test search functionality"""
    print("\n2. Testing: Search for 'Client'")
    response = requests.get(f"{BASE_URL}/transactions?filename={FILENAME}&search=Client")
    if response.status_code == 200:
        data = response.json()
        print(f"   [OK] Found {data['count']} transactions matching 'Client'")
    else:
        print(f"   [ERROR] Error: {response.status_code}")

def test_amount_filter():
    """Test amount filtering"""
    print("\n3. Testing: Filter by amount (1000-3000)")
    response = requests.get(f"{BASE_URL}/transactions?filename={FILENAME}&min_amount=1000&max_amount=3000")
    if response.status_code == 200:
        data = response.json()
        print(f"   [OK] Found {data['count']} transactions in range $1,000-$3,000")
    else:
        print(f"   [ERROR] Error: {response.status_code}")

def test_date_filter():
    """Test date filtering"""
    print("\n4. Testing: Filter by date (January 2026)")
    response = requests.get(f"{BASE_URL}/transactions?filename={FILENAME}&start_date=2026-01-01&end_date=2026-01-31")
    if response.status_code == 200:
        data = response.json()
        print(f"   [OK] Found {data['count']} transactions in January 2026")
    else:
        print(f"   [ERROR] Error: {response.status_code}")

def test_statistics():
    """Test statistics endpoint"""
    print("\n5. Testing: Get statistics")
    response = requests.get(f"{BASE_URL}/api/stats/{FILENAME}")
    if response.status_code == 200:
        data = response.json()
        stats = data['statistics']
        print(f"   [OK] Statistics retrieved:")
        print(f"     - Total Transactions: {stats['total_count']}")
        print(f"     - Total Amount: ${stats['total_amount']:,.2f}")
        print(f"     - Average Amount: ${stats['average_amount']:,.2f}")
    else:
        print(f"   ✗ Error: {response.status_code}")

def test_period_analysis():
    """Test period analysis"""
    print("\n6. Testing: Period analysis (monthly)")
    response = requests.get(f"{BASE_URL}/api/period-analysis/{FILENAME}?period=month")
    if response.status_code == 200:
        data = response.json()
        print(f"   [OK] Found {len(data['analysis'])} periods")
        for period in data['analysis'][:2]:  # Show first 2
            print(f"     {period['Period']}: ${period['Total']:,.2f}")
    else:
        print(f"   ✗ Error: {response.status_code}")

def test_health():
    """Test health check"""
    print("\n7. Testing: Health check")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        data = response.json()
        print(f"   [OK] Server is {data['status']} - Version {data['version']}")
    else:
        print(f"   [ERROR] Error: {response.status_code}")

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Month-End Automator API")
    print("=" * 60)
    print(f"\nTesting file: {FILENAME}")
    print("Make sure the server is running: python -m uvicorn main:app --reload\n")
    
    try:
        test_health()
        test_get_transactions()
        test_search()
        test_amount_filter()
        test_date_filter()
        test_statistics()
        test_period_analysis()
        
        print("\n" + "=" * 60)
        print("[OK] All tests completed!")
        print("=" * 60)
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Cannot connect to server!")
        print("   Please start the server first:")
        print("   python -m uvicorn main:app --reload")
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")

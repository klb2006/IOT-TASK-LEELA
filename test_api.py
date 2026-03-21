import requests
import json

BASE_URL = "http://127.0.0.1:8000"

endpoints = [
    "/api/v1/status",
    "/api/v1/sensor/latest",
    "/api/v1/model-info",
    "/api/v1/predictions-history",
]

print("Testing Backend API Endpoints")
print("=" * 60)

for endpoint in endpoints:
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        print(f"\n✓ {endpoint}")
        print(f"  Status: {response.status_code}")
        try:
            data = response.json()
            print(f"  Response: {json.dumps(data, indent=2)[:200]}...")
        except:
            print(f"  Response: {response.text[:200]}...")
    except Exception as e:
        print(f"\n✗ {endpoint}")
        print(f"  Error: {str(e)}")

print("\n" + "=" * 60)
print("Testing complete!")

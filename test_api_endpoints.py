#!/usr/bin/env python3
"""
Test script for Backend API endpoints
Tests: /api/v1/predict, /api/v1/model-info, /api/v1/predictions-history
"""

import requests
import json
from datetime import datetime
import time

# Configuration
BASE_URL = "http://127.0.0.1:8000"
API_VERSION = "v1"

# ANSI color codes for pretty output
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(title):
    """Print a formatted header"""
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{title:^60}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")

def print_success(msg):
    """Print success message"""
    print(f"{GREEN}✓ {msg}{RESET}")

def print_error(msg):
    """Print error message"""
    print(f"{RED}✗ {msg}{RESET}")

def print_info(msg):
    """Print info message"""
    print(f"{BLUE}ℹ {msg}{RESET}")

def print_test_section(title):
    """Print test section header"""
    print(f"\n{BOLD}{YELLOW}→ {title}{RESET}")

def test_api_status():
    """Test if API is running"""
    print_test_section("Checking API Status")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/status", timeout=5)
        if response.status_code == 200:
            print_success("API is running")
            print(f"  Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print_error(f"API returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to {BASE_URL}")
        print_info("Make sure the backend is running: python backend/main.py")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_predict_endpoint():
    """Test POST /api/v1/predict endpoint"""
    print_test_section("Testing POST /api/v1/predict")
    
    test_cases = [
        {
            "name": "Simple prediction with basic parameters",
            "data": {
                "distance": 24.5,
                "temperature": 28.3,
                "water_percent": 75.0,
                "time_features": [30, 14],
                "node_id": "test-node-1"
            }
        },
        {
            "name": "Prediction with different sensor values",
            "data": {
                "distance": 15.0,
                "temperature": 35.5,
                "water_percent": 90.0,
                "time_features": [45, 22],
                "node_id": "test-node-2"
            }
        },
        {
            "name": "Prediction with minimal parameters",
            "data": {
                "distance": 30.0,
                "temperature": 25.0
            }
        }
    ]
    
    all_passed = True
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n  Test {i}: {test_case['name']}")
        try:
            response = requests.post(
                f"{BASE_URL}/api/v{API_VERSION}/predict",
                json=test_case['data'],
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    print_success(f"Prediction received: {result.get('prediction')}")
                    print(f"    Confidence: {result.get('confidence', 'N/A')}")
                    print(f"    Timestamp: {result.get('timestamp', 'N/A')}")
                else:
                    print_error(f"API returned error: {result.get('message', 'Unknown error')}")
                    all_passed = False
            else:
                print_error(f"HTTP {response.status_code}: {response.text[:100]}")
                all_passed = False
        except requests.exceptions.Timeout:
            print_error("Request timed out (backend may be slow or unresponsive)")
            all_passed = False
        except Exception as e:
            print_error(f"Error: {str(e)}")
            all_passed = False
    
    return all_passed

def test_model_info_endpoint():
    """Test GET /api/v1/model-info endpoint"""
    print_test_section("Testing GET /api/v1/model-info")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v{API_VERSION}/model-info",
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                model_info = result.get('model_info', {})
                print_success("Model info retrieved successfully")
                print(f"  Model Type: {model_info.get('model_type', 'N/A')}")
                print(f"  Version: {model_info.get('version', 'N/A')}")
                print(f"  Accuracy: {model_info.get('accuracy', 'N/A')}")
                print(f"  Last Trained: {model_info.get('last_trained', 'N/A')}")
                print(f"  Input Features: {model_info.get('input_features', 'N/A')}")
                print(f"  Total Predictions: {model_info.get('total_predictions', 0)}")
                print(f"\n  Full Response:\n{json.dumps(result, indent=4)}")
                return True
            else:
                print_error(f"API returned error: {result.get('message', 'Unknown error')}")
                return False
        else:
            print_error(f"HTTP {response.status_code}: {response.text[:100]}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_predictions_history_endpoint():
    """Test GET /api/v1/predictions-history endpoint"""
    print_test_section("Testing GET /api/v1/predictions-history")
    
    try:
        # Test different limit values
        test_limits = [10, 50, 100]
        
        for limit in test_limits:
            print(f"\n  Testing with limit={limit}")
            response = requests.get(
                f"{BASE_URL}/api/v{API_VERSION}/predictions-history",
                params={'limit': limit},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    count = result.get('count', 0)
                    print_success(f"Retrieved {count} predictions (limit={limit})")
                    
                    # Show sample prediction if available
                    data = result.get('data', [])
                    if data and len(data) > 0:
                        sample = data[0]
                        print(f"    Sample prediction:")
                        print(f"      - Node ID: {sample.get('node_id', 'N/A')}")
                        print(f"      - Prediction: {sample.get('prediction', 'N/A')}")
                        print(f"      - Confidence: {sample.get('confidence', 'N/A')}")
                        print(f"      - Temperature: {sample.get('temperature', 'N/A')}°C")
                        print(f"      - Distance: {sample.get('distance', 'N/A')} cm")
                        print(f"      - Created: {sample.get('created_at', 'N/A')}")
                else:
                    print_error(f"API returned error: {result.get('message', 'Unknown error')}")
                    return False
            else:
                print_error(f"HTTP {response.status_code}: {response.text[:100]}")
                return False
        
        return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_invalid_requests():
    """Test error handling with invalid requests"""
    print_test_section("Testing Error Handling")
    
    test_cases = [
        {
            "name": "Missing distance parameter",
            "data": {
                "temperature": 28.3,
                "water_percent": 75.0
            }
        },
        {
            "name": "Missing temperature parameter",
            "data": {
                "distance": 24.5,
                "water_percent": 75.0
            }
        },
        {
            "name": "Invalid data types",
            "data": {
                "distance": "twenty-four",
                "temperature": "warm"
            }
        }
    ]
    
    all_handled = True
    for test_case in test_cases:
        print(f"\n  Test: {test_case['name']}")
        try:
            response = requests.post(
                f"{BASE_URL}/api/v{API_VERSION}/predict",
                json=test_case['data'],
                timeout=5
            )
            
            if response.status_code >= 400 or response.json().get('status') == 'error':
                print_success(f"Error properly handled")
                print(f"    Message: {response.json().get('message', 'No message')}")
            else:
                print_error(f"Invalid request was not rejected")
                all_handled = False
        except Exception as e:
            print_success(f"Error properly caught: {str(e)[:50]}")
    
    return all_handled

def main():
    """Run all tests"""
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}Backend API Endpoint Tests{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"Testing: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Track results
    results = {}
    
    # Test 1: API Status
    print_header("Test 1: API Status")
    results['api_status'] = test_api_status()
    
    if not results['api_status']:
        print_error("Cannot proceed - API is not running")
        return
    
    # Test 2: Predict Endpoint
    print_header("Test 2: Prediction Endpoint (/api/v1/predict)")
    results['predict'] = test_predict_endpoint()
    
    # Test 3: Model Info Endpoint
    print_header("Test 3: Model Info Endpoint (/api/v1/model-info)")
    results['model_info'] = test_model_info_endpoint()
    
    # Test 4: Predictions History Endpoint
    print_header("Test 4: Predictions History Endpoint (/api/v1/predictions-history)")
    results['history'] = test_predictions_history_endpoint()
    
    # Test 5: Error Handling
    print_header("Test 5: Error Handling")
    results['error_handling'] = test_invalid_requests()
    
    # Summary
    print_header("Test Summary")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = f"{GREEN}✓ PASSED{RESET}" if result else f"{RED}✗ FAILED{RESET}"
        print(f"  {test:30} {status}")
    
    print(f"\n  {BOLD}Total: {passed}/{total} tests passed{RESET}")
    
    if passed == total:
        print(f"\n{GREEN}{BOLD}✓ All tests passed!{RESET}")
    else:
        print(f"\n{YELLOW}{BOLD}⚠ Some tests failed - check output above{RESET}")
    
    print(f"\n{BLUE}For more details, visit: {BASE_URL}/docs{RESET}\n")

if __name__ == "__main__":
    main()

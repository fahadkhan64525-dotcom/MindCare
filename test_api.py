"""
MindCare API Testing Guide
Examples for testing all endpoints
"""

import requests
import json
from datetime import datetime

# Base URL
BASE_URL = "http://localhost:5000"

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    END = '\033[0m'


def print_section(title):
    """Print a formatted section title"""
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.CYAN}{title}{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")


def print_request(method, endpoint, data=None):
    """Print request details"""
    print(f"{Colors.YELLOW}→ {method} {endpoint}{Colors.END}")
    if data:
        print(f"{Colors.YELLOW}Request Body:{Colors.END}")
        print(json.dumps(data, indent=2))


def print_response(response):
    """Print response details"""
    print(f"{Colors.GREEN}✓ Status: {response.status_code}{Colors.END}")
    print(f"{Colors.GREEN}Response:{Colors.END}")
    
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)


def test_home():
    """Test home endpoint"""
    print_section("TEST 1: Home Endpoint")
    
    endpoint = f"{BASE_URL}/"
    print_request("GET", "/")
    
    response = requests.get(endpoint)
    print_response(response)
    
    return response.status_code == 200


def test_health():
    """Test health check endpoint"""
    print_section("TEST 2: Health Check")
    
    endpoint = f"{BASE_URL}/health"
    print_request("GET", "/health")
    
    response = requests.get(endpoint)
    print_response(response)
    
    return response.status_code == 200


def test_predict_success():
    """Test successful stress prediction"""
    print_section("TEST 3: Predict Stress (Success Case)")
    
    endpoint = f"{BASE_URL}/predict"
    data = {
        "mood": "stressed",
        "sleep": 5.5,
        "screen_time": 10,
        "workload": 12
    }
    
    print_request("POST", "/predict", data)
    
    response = requests.post(endpoint, json=data)
    print_response(response)
    
    return response.status_code == 200


def test_predict_good_condition():
    """Test prediction with good conditions"""
    print_section("TEST 4: Predict Stress (Good Conditions)")
    
    endpoint = f"{BASE_URL}/predict"
    data = {
        "mood": "happy",
        "sleep": 8.5,
        "screen_time": 4,
        "workload": 6
    }
    
    print_request("POST", "/predict", data)
    
    response = requests.post(endpoint, json=data)
    print_response(response)
    
    return response.status_code == 200


def test_predict_all_moods():
    """Test all mood options"""
    print_section("TEST 5: Predict with All Moods")
    
    moods = ["happy", "neutral", "sad", "stressed"]
    results = {}
    
    for mood in moods:
        print(f"\n{Colors.YELLOW}Testing mood: {mood}{Colors.END}")
        
        endpoint = f"{BASE_URL}/predict"
        data = {
            "mood": mood,
            "sleep": 7,
            "screen_time": 6,
            "workload": 8
        }
        
        response = requests.post(endpoint, json=data)
        results[mood] = {
            "status_code": response.status_code,
            "stress_level": response.json().get("stress_level", "ERROR")
        }
        print(f"{Colors.GREEN}Stress Level: {results[mood]['stress_level']}{Colors.END}")
    
    return all(r["status_code"] == 200 for r in results.values())


def test_predict_validation():
    """Test input validation"""
    print_section("TEST 6: Input Validation")
    
    test_cases = [
        {
            "name": "Missing mood",
            "data": {"sleep": 7, "screen_time": 6, "workload": 8}
        },
        {
            "name": "Invalid mood",
            "data": {"mood": "invalid", "sleep": 7, "screen_time": 6, "workload": 8}
        },
        {
            "name": "Invalid sleep value",
            "data": {"mood": "happy", "sleep": "abc", "screen_time": 6, "workload": 8}
        },
        {
            "name": "Sleep out of range",
            "data": {"mood": "happy", "sleep": 30, "screen_time": 6, "workload": 8}
        }
    ]
    
    endpoint = f"{BASE_URL}/predict"
    results = {}
    
    for test_case in test_cases:
        print(f"\n{Colors.YELLOW}Testing: {test_case['name']}{Colors.END}")
        print_request("POST", "/predict", test_case["data"])
        
        response = requests.post(endpoint, json=test_case["data"])
        results[test_case["name"]] = response.status_code
        
        print(f"{Colors.GREEN}Status: {response.status_code}{Colors.END}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Should all return error (4xx status)
    return all(status >= 400 for status in results.values())


def test_chat():
    """Test chat endpoint"""
    print_section("TEST 7: Chat Endpoint")
    
    test_messages = [
        "I'm feeling very stressed about work",
        "I can't sleep well",
        "I feel sad and lonely",
        "How can I manage my anxiety?",
        "What should I do?",
        "Hello, how are you?"
    ]
    
    endpoint = f"{BASE_URL}/chat"
    
    for message in test_messages:
        print(f"\n{Colors.YELLOW}Message: {message}{Colors.END}")
        
        data = {"message": message}
        print_request("POST", "/chat", data)
        
        response = requests.post(endpoint, json=data)
        
        if response.status_code == 200:
            json_response = response.json()
            print(f"{Colors.GREEN}Category: {json_response.get('category', 'N/A')}{Colors.END}")
            print(f"{Colors.GREEN}Response: {json_response.get('response', 'N/A')}{Colors.END}")
        else:
            print_response(response)
    
    return True


def test_history():
    """Test history endpoint"""
    print_section("TEST 8: Get History")
    
    # First add some entries
    print(f"{Colors.YELLOW}Adding test entries...{Colors.END}\n")
    
    entries = [
        {"mood": "happy", "sleep": 8, "screen_time": 5, "workload": 7},
        {"mood": "neutral", "sleep": 7, "screen_time": 6, "workload": 8},
        {"mood": "stressed", "sleep": 5, "screen_time": 10, "workload": 12}
    ]
    
    for entry in entries:
        requests.post(f"{BASE_URL}/predict", json=entry)
    
    # Get history
    endpoint = f"{BASE_URL}/history?limit=5"
    print_request("GET", "/history?limit=5")
    
    response = requests.get(endpoint)
    print_response(response)
    
    return response.status_code == 200


def test_analytics():
    """Test analytics endpoint"""
    print_section("TEST 9: Analytics")
    
    endpoint = f"{BASE_URL}/analytics"
    print_request("GET", "/analytics")
    
    response = requests.get(endpoint)
    print_response(response)
    
    return response.status_code == 200


def test_error_handling():
    """Test error handling"""
    print_section("TEST 10: Error Handling")
    
    # Test invalid JSON
    print(f"\n{Colors.YELLOW}Testing invalid JSON...{Colors.END}")
    
    endpoint = f"{BASE_URL}/predict"
    response = requests.post(endpoint, json=None)
    print(f"Status: {response.status_code}")
    
    # Test not found
    print(f"\n{Colors.YELLOW}Testing 404 Not Found...{Colors.END}")
    
    response = requests.get(f"{BASE_URL}/nonexistent")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return True


def run_all_tests():
    """Run all tests"""
    print(f"\n{Colors.CYAN}")
    print("╔════════════════════════════════════════════════════════╗")
    print("║     MindCare API - Comprehensive Testing Suite         ║")
    print("╚════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    tests = [
        ("Home Endpoint", test_home),
        ("Health Check", test_health),
        ("Predict Stress (Success)", test_predict_success),
        ("Predict Stress (Good Conditions)", test_predict_good_condition),
        ("All Moods", test_predict_all_moods),
        ("Input Validation", test_predict_validation),
        ("Chat", test_chat),
        ("History", test_history),
        ("Analytics", test_analytics),
        ("Error Handling", test_error_handling)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except requests.exceptions.ConnectionError:
            print(f"\n{Colors.RED}ERROR: Cannot connect to API at {BASE_URL}{Colors.END}")
            print(f"{Colors.RED}Make sure the server is running: python run.py{Colors.END}")
            return False
        except Exception as e:
            print(f"\n{Colors.RED}ERROR in {test_name}: {str(e)}{Colors.END}")
            results[test_name] = False
    
    # Print summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"Passed: {Colors.GREEN}{passed}/{total}{Colors.END}\n")
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if result else f"{Colors.RED}✗ FAIL{Colors.END}"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*60}\n")
    
    return passed == total


if __name__ == "__main__":
    import sys
    
    # Check if API is running
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
    except:
        print(f"{Colors.RED}ERROR: Cannot reach API at {BASE_URL}{Colors.END}")
        print(f"Please start the server first:")
        print(f"  python run.py")
        sys.exit(1)
    
    # Run tests
    success = run_all_tests()
    sys.exit(0 if success else 1)

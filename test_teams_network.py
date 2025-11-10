"""
Test script to verify Teams Integration and API accessibility
"""

import requests
import sys

# Configuration
API_BASE_URL = "http://192.168.1.3:5000"
LOCALHOST_URL = "http://localhost:5000"

def test_endpoint(url, endpoint_name):
    """Test if an endpoint is accessible"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {endpoint_name}: OK")
            return True
        else:
            print(f"⚠️  {endpoint_name}: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {endpoint_name}: Connection refused (server not running?)")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {endpoint_name}: Timeout")
        return False
    except Exception as e:
        print(f"❌ {endpoint_name}: {str(e)}")
        return False

def main():
    print("="*60)
    print("Teams Integration & Network Accessibility Test")
    print("="*60)
    print()
    
    # Test localhost
    print("Testing localhost access...")
    localhost_ok = test_endpoint(f"{LOCALHOST_URL}/health", "Localhost (/health)")
    print()
    
    # Test network IP
    print("Testing network IP access (for Teams)...")
    network_ok = test_endpoint(f"{API_BASE_URL}/health", "Network IP (/health)")
    print()
    
    # Test specific endpoints for Teams
    if network_ok:
        print("Testing Teams integration endpoints...")
        test_endpoint(f"{API_BASE_URL}/api/watcher/status", "Watcher Status")
        test_endpoint(f"{API_BASE_URL}/", "API Documentation")
        print()
    
    # Summary
    print("="*60)
    print("Test Summary")
    print("="*60)
    
    if localhost_ok and network_ok:
        print("✅ All tests passed!")
        print()
        print("Your Teams adaptive card buttons should work with:")
        print(f"   {API_BASE_URL}")
        print()
        print("URLs generated for Teams:")
        print(f"   View:    {API_BASE_URL}/api/invoice/view/{{filename}}")
        print(f"   Approve: {API_BASE_URL}/api/invoice/approve/{{filename}}")
        print(f"   Reject:  {API_BASE_URL}/api/invoice/reject/{{filename}}")
        
    elif localhost_ok and not network_ok:
        print("⚠️  Server is running but not accessible from network!")
        print()
        print("Possible issues:")
        print("  1. Windows Firewall is blocking port 5000")
        print("     Solution: Run setup_firewall.ps1 as Administrator")
        print()
        print("  2. IP address has changed")
        print("     Solution: Run 'ipconfig' and update API_BASE_URL in app.py")
        print()
        print("  3. Antivirus software is blocking connections")
        print("     Solution: Add exception for Python/Flask on port 5000")
        
    else:
        print("❌ Server is not running!")
        print()
        print("Start the server with: python app.py")
    
    print("="*60)
    print()

if __name__ == "__main__":
    main()

"""
Test script to verify the combined Invoice AI system
"""
import sys
import os
import json
import requests
import time
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

def test_database_operations():
    """Test database operations"""
    print("🔧 Testing database operations...")
    
    try:
        from database import RequestRepository
        repo = RequestRepository()
        
        # Test create request
        request = repo.create_request(
            user_id="TEST_USER",
            total_amount=1500.00,
            invoice_date="2024-11-04",
            invoice_number="INV-12345",
            category_name="Office Supplies",
            comments="Test request creation",
            approval_type="Manual",
            created_by="TEST"
        )
        
        print(f"✓ Request created: ID {request.ID}")
        
        # Test get request
        retrieved = repo.get_request(request.ID)
        print(f"✓ Request retrieved: {retrieved.INVOICE_NUMBER}")
        
        # Test update status
        updated = repo.update_request_status(
            request.ID, 
            "Approved", 
            "Test approval", 
            "ADMIN"
        )
        print(f"✓ Request updated: Status {updated.CURRENT_STATUS}")
        
        # Test list requests
        requests_list, total = repo.list_requests(1, 10)
        print(f"✓ Listed {len(requests_list)} requests, total: {total}")
        
        # Test insights
        insights = repo.get_insights()
        print(f"✓ Insights: {insights}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        return False


def test_request_service():
    """Test request service"""
    print("\n🔧 Testing request service...")
    
    try:
        from services.request_service import RequestService
        service = RequestService()
        
        # Test create from invoice data
        invoice_data = {
            'total_amount': 2500.00,
            'invoice_date': '2024-11-04',
            'invoice_number': 'INV-67890',
            'category_name': 'Travel',
            'approval_info': {
                'status': 'pending'
            }
        }
        
        request = service.create_request_from_invoice(
            user_id="AI_USER",
            invoice_data=invoice_data,
            approval_status="Pending",
            created_by="AI"
        )
        
        print(f"✓ Service request created: ID {request.ID}")
        
        # Test get insights
        insights = service.get_insights()
        print(f"✓ Service insights: {insights}")
        
        return True
        
    except Exception as e:
        print(f"❌ Service test failed: {str(e)}")
        return False


def test_api_endpoints():
    """Test API endpoints (requires server to be running)"""
    print("\n🔧 Testing API endpoints...")
    
    base_url = "http://localhost:8000"
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✓ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test root endpoint
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Root endpoint working: {data.get('service')}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
        
        # Test requests API
        response = requests.get(f"{base_url}/api/requests/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Requests API working: {data.get('total', 0)} requests")
        else:
            print(f"❌ Requests API failed: {response.status_code}")
        
        # Test insights API
        response = requests.get(f"{base_url}/api/requests/insights/summary", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Insights API working: {data.get('total', 0)} total requests")
        else:
            print(f"❌ Insights API failed: {response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: python combined_app.py")
        return False
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        return False


def main():
    """Main test function"""
    print("="*60)
    print("Invoice AI System Test")
    print("="*60)
    
    # Test database operations
    db_success = test_database_operations()
    
    # Test service layer
    service_success = test_request_service()
    
    # Test API endpoints (optional - requires server)
    api_success = test_api_endpoints()
    
    print("\n" + "="*60)
    print("Test Results:")
    print(f"  Database Operations: {'✓ PASS' if db_success else '❌ FAIL'}")
    print(f"  Service Layer:       {'✓ PASS' if service_success else '❌ FAIL'}")
    print(f"  API Endpoints:       {'✓ PASS' if api_success else '❌ FAIL (server may not be running)'}")
    print("="*60)
    
    if db_success and service_success:
        print("\n🎉 Core system is working! You can now:")
        print("   1. Start the server: python combined_app.py")
        print("   2. Process invoices: they will be saved to database")
        print("   3. Access API docs: http://localhost:8000/docs")
        print("   4. View requests: http://localhost:8000/api/requests/")
    else:
        print("\n❌ Some components failed. Please check the errors above.")


if __name__ == "__main__":
    main()
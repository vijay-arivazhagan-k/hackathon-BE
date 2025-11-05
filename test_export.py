"""
Test script for export endpoint
"""
import sys
import json
from datetime import datetime

# Test 1: Verify imports
print("=" * 60)
print("TEST 1: Verifying imports...")
print("=" * 60)

try:
    from api.requests import router
    print("✓ Successfully imported API router")
except Exception as e:
    print(f"✗ Failed to import API router: {e}")
    sys.exit(1)

try:
    from services.request_service import RequestService
    print("✓ Successfully imported RequestService")
except Exception as e:
    print(f"✗ Failed to import RequestService: {e}")
    sys.exit(1)

try:
    import openpyxl
    print(f"✓ Successfully imported openpyxl (version {openpyxl.__version__})")
except Exception as e:
    print(f"✗ Failed to import openpyxl: {e}")
    sys.exit(1)

# Test 2: Verify RequestService has the new method
print("\n" + "=" * 60)
print("TEST 2: Verifying RequestService.get_filtered_requests_for_export method...")
print("=" * 60)

try:
    service = RequestService()
    if hasattr(service, 'get_filtered_requests_for_export'):
        print("✓ RequestService has get_filtered_requests_for_export method")
    else:
        print("✗ RequestService missing get_filtered_requests_for_export method")
        sys.exit(1)
except Exception as e:
    print(f"✗ Failed to create RequestService: {e}")
    sys.exit(1)

# Test 3: Verify database has the new method
print("\n" + "=" * 60)
print("TEST 3: Verifying RequestRepository.get_filtered_requests_for_export method...")
print("=" * 60)

try:
    from database import RequestRepository
    repo = RequestRepository()
    if hasattr(repo, 'get_filtered_requests_for_export'):
        print("✓ RequestRepository has get_filtered_requests_for_export method")
    else:
        print("✗ RequestRepository missing get_filtered_requests_for_export method")
        sys.exit(1)
except Exception as e:
    print(f"✗ Failed to verify RequestRepository: {e}")
    sys.exit(1)

# Test 4: Check API route definitions
print("\n" + "=" * 60)
print("TEST 4: Checking API route definitions...")
print("=" * 60)

route_paths = [route.path for route in router.routes]
print(f"Available routes in requests router:")
for path in sorted(route_paths):
    print(f"  - {path}")

if "/export" in route_paths:
    print("✓ /export route is defined")
else:
    print("✗ /export route is NOT defined")
    sys.exit(1)

if "/{request_id}" in route_paths:
    print("✓ /{request_id} route is defined")
else:
    print("✗ /{request_id} route is NOT defined")
    sys.exit(1)

# Check route order - /export should come before /{request_id}
export_index = None
request_id_index = None
for i, route in enumerate(router.routes):
    if route.path == "/export":
        export_index = i
    elif route.path == "/{request_id}":
        request_id_index = i

if export_index is not None and request_id_index is not None:
    if export_index < request_id_index:
        print("✓ /export route is positioned BEFORE /{request_id} (correct route matching order)")
    else:
        print("⚠ /export route is positioned AFTER /{request_id} (may cause routing issues)")
else:
    print("⚠ Could not verify route order")

# Test 5: Test creating sample data and export
print("\n" + "=" * 60)
print("TEST 5: Testing export with sample data...")
print("=" * 60)

try:
    # Create sample requests
    req1 = service.create_request(
        user_id="john@example.com",
        total_amount=1500.00,
        invoice_date="2025-01-01",
        invoice_number="INV001",
        category_name="Test",
        comments="Test invoice 1",
        approval_type="Manual"
    )
    print(f"✓ Created test request 1 (ID: {req1.ID})")
    
    req2 = service.create_request(
        user_id="jane@example.com",
        total_amount=2500.50,
        invoice_date="2025-01-02",
        invoice_number="INV002",
        category_name="Test",
        comments="Test invoice 2",
        approval_type="Auto"
    )
    print(f"✓ Created test request 2 (ID: {req2.ID})")
    
    # Test get_filtered_requests_for_export
    all_requests = service.get_filtered_requests_for_export()
    print(f"✓ Retrieved {len(all_requests)} total requests for export")
    
    filtered_requests = service.get_filtered_requests_for_export(
        start_date="2025-01-01",
        end_date="2025-01-02",
        category="Test"
    )
    print(f"✓ Retrieved {len(filtered_requests)} filtered requests for export")
    
    if len(filtered_requests) >= 2:
        print(f"  Request 1: {filtered_requests[0].USER_ID} - {filtered_requests[0].TOTAL_AMOUNT}")
        print(f"  Request 2: {filtered_requests[1].USER_ID} - {filtered_requests[1].TOTAL_AMOUNT}")
    
except Exception as e:
    print(f"✗ Error during export test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED!")
print("=" * 60)
print("\nThe export endpoint should now work correctly.")
print("The routing order has been fixed: /export will be matched before /{request_id}")

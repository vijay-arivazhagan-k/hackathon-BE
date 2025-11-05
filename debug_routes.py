#!/usr/bin/env python
"""Debug script to check if routes are properly registered"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 70)
print("DEBUGGING ROUTE REGISTRATION")
print("=" * 70)

try:
    print("\n1. Importing api.categories router...")
    from api.categories import router as cat_router
    print(f"   ✓ Categories router imported")
    print(f"     - Prefix: {cat_router.prefix}")
    print(f"     - Routes: {len(cat_router.routes)}")
    for route in cat_router.routes:
        if hasattr(route, 'path'):
            print(f"       • {route.path}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n2. Importing api.requests router...")
    from api.requests import router as req_router
    print(f"   ✓ Requests router imported")
    print(f"     - Prefix: {req_router.prefix}")
    print(f"     - Routes: {len(req_router.routes)}")
except Exception as e:
    print(f"   ✗ Error: {e}")

try:
    print("\n3. Creating combined app...")
    from combined_app import create_combined_app
    app = create_combined_app()
    print(f"   ✓ Combined app created")
    
    print("\n4. Checking registered routes in main app...")
    api_routes = [r for r in app.routes if hasattr(r, 'path') and '/api/categor' in str(r.path)]
    print(f"   Found {len(api_routes)} category routes")
    
    for route in app.routes:
        if hasattr(route, 'path'):
            path = getattr(route, 'path', 'unknown')
            if 'categor' in str(path).lower():
                print(f"     • {path}")
    
    print("\n5. Checking if POST /api/categories/ is available...")
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    # Test if route exists
    response = client.options("/api/categories/")
    print(f"   OPTIONS /api/categories/ -> {response.status_code}")
    
    # Try to post
    response = client.post(
        "/api/categories/",
        data={
            "categoryname": "TEST",
            "categorydescription": "Test",
            "status": "true"
        }
    )
    print(f"   POST /api/categories/ -> {response.status_code}")
    if response.status_code == 404:
        print(f"   ✗ ROUTE NOT FOUND!")
        print("\n   All available routes:")
        for route in app.routes:
            if hasattr(route, 'path'):
                print(f"     • {route.path}")
    else:
        print(f"   ✓ Route found: {response.status_code}")
        
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)

#!/usr/bin/env python
"""
Quick test to verify the categories API is working
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from combined_app import create_combined_app
from fastapi.testclient import TestClient

# Create the combined app
app = create_combined_app()

# Create a test client
client = TestClient(app)

print("Testing Categories API...")
print("-" * 60)

# Test 1: Check if the POST endpoint is available
print("\n1. Testing POST /api/categories/")
response = client.post(
    "/api/categories/",
    data={
        "categoryname": "Test Category",
        "categorydescription": "Test Description",
        "maximumamount": 1000.00,
        "status": True,
        "approval_criteria": "Test Criteria"
    }
)
print(f"   Status Code: {response.status_code}")
print(f"   Response: {response.json() if response.status_code != 404 else 'NOT FOUND'}")

# Test 2: Check if GET endpoint is available
print("\n2. Testing GET /api/categories/")
response = client.get("/api/categories/")
print(f"   Status Code: {response.status_code}")
print(f"   Response: {response.json() if response.status_code != 404 else 'NOT FOUND'}")

print("\n" + "-" * 60)
print("Testing complete!")

# List all routes
print("\nAvailable routes:")
for route in app.routes:
    if hasattr(route, 'path') and 'api' in route.path:
        methods = getattr(route, 'methods', set()) or {'GET'}
        print(f"  {route.path:30} {methods}")

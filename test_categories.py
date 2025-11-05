"""
Test script for Category API with approval criteria
Demonstrates all CRUD operations
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8001/api"

def test_create_category():
    """Test creating a category with approval criteria"""
    print("\n=== TEST 1: CREATE CATEGORY ===")
    
    data = {
        'categoryname': 'TRAVEL',
        'categorydescription': 'Travel and transportation expenses',
        'maximumamount': 5000.00,
        'status': 'true',
        'approval_criteria': 'All travel must be pre-approved by manager. Flights must be economy class. Hotels must be within per-diem limits.'
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/categories/",
            data=data,
            timeout=10
        )
        
        if response.status_code == 201:
            category = response.json()
            print(f"✅ Category created successfully")
            print(f"   ID: {category.get('id')}")
            print(f"   Name: {category.get('categoryname')}")
            print(f"   Approval Criteria: {category.get('approval_criteria')}")
            return category.get('id')
        else:
            print(f"❌ Failed to create category: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_get_categories():
    """Test getting list of categories"""
    print("\n=== TEST 2: GET CATEGORIES ===")
    
    try:
        response = requests.get(
            f"{BASE_URL}/categories/?page=1&page_size=20",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved {len(data.get('items', []))} categories")
            
            for cat in data.get('items', [])[:3]:  # Show first 3
                print(f"\n   Category: {cat.get('categoryname')}")
                print(f"   Approval Criteria: {cat.get('approval_criteria', 'N/A')}")
                print(f"   Max Amount: {cat.get('maximumamount')}")
                print(f"   Status: {cat.get('status')}")
        else:
            print(f"❌ Failed to get categories: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_get_category(category_id):
    """Test getting a single category"""
    print(f"\n=== TEST 3: GET SINGLE CATEGORY (ID: {category_id}) ===")
    
    try:
        response = requests.get(
            f"{BASE_URL}/categories/{category_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            cat = response.json()
            print(f"✅ Retrieved category: {cat.get('categoryname')}")
            print(f"   Description: {cat.get('categorydescription')}")
            print(f"   Approval Criteria: {cat.get('approval_criteria')}")
            print(f"   Max Amount: {cat.get('maximumamount')}")
            print(f"   Status: {cat.get('status')}")
            print(f"   Created On: {cat.get('createdon')}")
            print(f"   Created By: {cat.get('createdby')}")
        else:
            print(f"❌ Failed to get category: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_update_category(category_id):
    """Test updating a category"""
    print(f"\n=== TEST 4: UPDATE CATEGORY (ID: {category_id}) ===")
    
    data = {
        'maximumamount': '6000.00',
        'approval_criteria': 'UPDATED: All travel must be pre-approved. Flights must be economy class. Hotels max $150/night.',
        'comments': 'Updated approval criteria and maximum amount'
    }
    
    try:
        response = requests.patch(
            f"{BASE_URL}/categories/{category_id}",
            data=data,
            timeout=10
        )
        
        if response.status_code == 200:
            cat = response.json()
            print(f"✅ Category updated successfully")
            print(f"   New Max Amount: {cat.get('maximumamount')}")
            print(f"   New Approval Criteria: {cat.get('approval_criteria')}")
            print(f"   Updated On: {cat.get('updatedon')}")
            print(f"   Updated By: {cat.get('updatedby')}")
        else:
            print(f"❌ Failed to update category: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_get_history(category_id):
    """Test getting category history"""
    print(f"\n=== TEST 5: GET CATEGORY HISTORY (ID: {category_id}) ===")
    
    try:
        response = requests.get(
            f"{BASE_URL}/categories/{category_id}/history",
            timeout=10
        )
        
        if response.status_code == 200:
            history = response.json()
            print(f"✅ Retrieved {len(history)} history records")
            
            for i, record in enumerate(history, 1):
                print(f"\n   Record {i}:")
                print(f"   Comments: {record.get('comments')}")
                print(f"   Approval Criteria: {record.get('approval_criteria', 'N/A')}")
                print(f"   Max Amount: {record.get('maximumamount')}")
                print(f"   Created On: {record.get('createdon')}")
                print(f"   Created By: {record.get('createdby')}")
        else:
            print(f"❌ Failed to get history: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_uppercase_conversion():
    """Test that category name is converted to uppercase"""
    print("\n=== TEST 6: UPPERCASE CONVERSION ===")
    
    data = {
        'categoryname': 'meals and entertainment',  # lowercase input
        'categorydescription': 'Meal and entertainment expenses',
        'approval_criteria': 'Meals must be documented. Alcohol limited to team events.'
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/categories/",
            data=data,
            timeout=10
        )
        
        if response.status_code == 201:
            cat = response.json()
            stored_name = cat.get('categoryname')
            expected_name = 'MEALS AND ENTERTAINMENT'
            
            if stored_name == expected_name:
                print(f"✅ Category name correctly converted to uppercase")
                print(f"   Input: {data['categoryname']}")
                print(f"   Stored: {stored_name}")
            else:
                print(f"❌ Category name not converted correctly")
                print(f"   Input: {data['categoryname']}")
                print(f"   Expected: {expected_name}")
                print(f"   Got: {stored_name}")
        else:
            print(f"❌ Failed to create category: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    print("=" * 60)
    print("CATEGORY API TEST SUITE - WITH APPROVAL CRITERIA")
    print("=" * 60)
    
    # Run tests
    cat_id = test_create_category()
    
    if cat_id:
        test_get_categories()
        test_get_category(cat_id)
        test_update_category(cat_id)
        test_get_history(cat_id)
    
    test_uppercase_conversion()
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETED")
    print("=" * 60)

"""
Test approval rules
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from invoice_processor import InvoiceProcessor


def test_approval_rules():
    """Test various approval scenarios."""
    
    print("="*70)
    print("Invoice Approval Rules Test")
    print("="*70)
    print("\nRules:")
    print("  ✅ APPROVED if: Items < 5 AND Amount < $2000")
    print("  ⏳ PENDING if: Items >= 5 OR Amount >= $2000")
    print("\n" + "="*70)
    
    # Initialize processor (will use config.json)
    processor = InvoiceProcessor()
    
    # Test cases
    test_cases = [
        {
            "name": "Small invoice - Should be APPROVED",
            "data": {
                "items": [
                    {"item_name": "Item 1", "item_price": "$100.00"},
                    {"item_name": "Item 2", "item_price": "$200.00"}
                ],
                "total_price": "$300.00"
            },
            "expected": "approved"
        },
        {
            "name": "High amount - Should be PENDING",
            "data": {
                "items": [
                    {"item_name": "Item 1", "item_price": "$1,500.00"}
                ],
                "total_price": "$2,500.00"
            },
            "expected": "pending"
        },
        {
            "name": "Too many items - Should be PENDING",
            "data": {
                "items": [
                    {"item_name": "Item 1", "item_price": "$100.00"},
                    {"item_name": "Item 2", "item_price": "$100.00"},
                    {"item_name": "Item 3", "item_price": "$100.00"},
                    {"item_name": "Item 4", "item_price": "$100.00"},
                    {"item_name": "Item 5", "item_price": "$100.00"}
                ],
                "total_price": "$500.00"
            },
            "expected": "pending"
        }
    ]
    
    passed = 0
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['name']}")
        approval_info = processor.check_approval_status(test['data'])
        
        status_icon = "✅" if approval_info['status'] == test['expected'] else "❌"
        print(f"  {status_icon} Status: {approval_info['status'].upper()}")
        print(f"     Items: {approval_info['item_count']} | Amount: ${approval_info['total_amount']:.2f}")
        
        if approval_info['status'] == test['expected']:
            passed += 1
    
    print(f"\n{'='*70}")
    print(f"Result: {passed}/{len(test_cases)} tests passed")
    print("="*70)


if __name__ == "__main__":
    test_approval_rules()

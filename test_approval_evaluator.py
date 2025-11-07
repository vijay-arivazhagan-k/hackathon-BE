"""
Test script for approval evaluator
"""
import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services'))
sys.path.insert(0, os.path.dirname(__file__))

from services.approval_evaluator import ApprovalEvaluator


def test_category_extraction():
    """Test category name extraction from filenames"""
    print("\n" + "="*60)
    print("TEST 1: Category Extraction from Filename")
    print("="*60)
    
    evaluator = ApprovalEvaluator()
    
    test_cases = [
        ("GBS09500_TRAVEL.pdf", "TRAVEL"),
        ("GBS09500_MEALS.png", "MEALS"),
        ("GBS09500_OFFICE_SUPPLIES.jpg", "OFFICE_SUPPLIES"),
        ("SimpleName.pdf", "General"),  # No underscore
    ]
    
    for filename, expected in test_cases:
        result = evaluator.extract_category_from_filename(filename)
        status = "✓" if result == expected else "✗"
        print(f"{status} {filename:30} -> {result:20} (expected: {expected})")


def test_invoice_evaluation():
    """Test invoice evaluation logic"""
    print("\n" + "="*60)
    print("TEST 2: Invoice Evaluation Logic")
    print("="*60)
    
    evaluator = ApprovalEvaluator()
    
    # Test case 1: Should be approved (low amount, few items)
    invoice_1 = {
        'total_amount': 1500.0,
        'total_price': '$1500.00',
        'items': [
            {'item_name': 'Item 1', 'item_price': '$500'},
            {'item_name': 'Item 2', 'item_price': '$1000'},
        ]
    }
    
    result_1 = evaluator.evaluate_invoice(invoice_1)
    print(f"\n✓ Test Case 1: Low amount, few items")
    print(f"  Decision: {result_1['decision']}")
    print(f"  Reasons: {', '.join(result_1['reasons'])}")
    assert result_1['decision'] == 'Approved', "Should be approved"
    
    # Test case 2: Should be pending (high amount)
    invoice_2 = {
        'total_amount': 3000.0,
        'total_price': '$3000.00',
        'items': [
            {'item_name': 'Item 1', 'item_price': '$1500'},
            {'item_name': 'Item 2', 'item_price': '$1500'},
        ]
    }
    
    result_2 = evaluator.evaluate_invoice(invoice_2)
    print(f"\n✓ Test Case 2: High amount")
    print(f"  Decision: {result_2['decision']}")
    print(f"  Reasons: {', '.join(result_2['reasons'])}")
    assert result_2['decision'] == 'Pending', "Should be pending"
    
    # Test case 3: Should be pending (many items)
    invoice_3 = {
        'total_amount': 500.0,
        'total_price': '$500.00',
        'items': [
            {'item_name': f'Item {i}', 'item_price': '$50'} for i in range(8)
        ]
    }
    
    result_3 = evaluator.evaluate_invoice(invoice_3)
    print(f"\n✓ Test Case 3: Many items")
    print(f"  Decision: {result_3['decision']}")
    print(f"  Reasons: {', '.join(result_3['reasons'])}")
    assert result_3['decision'] == 'Pending', "Should be pending"
    
    print(f"\n✓ All evaluation tests passed!")


def test_full_workflow():
    """Test full evaluation workflow"""
    print("\n" + "="*60)
    print("TEST 3: Full Evaluation Workflow")
    print("="*60)
    
    evaluator = ApprovalEvaluator()
    
    filename = "GBS09500_TRAVEL.pdf"
    invoice_data = {
        'invoice_number': 'INV-12345',
        'invoice_date': '2024-11-05',
        'total_amount': 1800.0,
        'total_price': '$1800.00',
        'items': [
            {'item_name': 'Flight', 'item_price': '$1200'},
            {'item_name': 'Hotel', 'item_price': '$600'},
        ]
    }
    
    print(f"\nProcessing: {filename}")
    print(f"Invoice Data:")
    print(f"  - Number: {invoice_data['invoice_number']}")
    print(f"  - Date: {invoice_data['invoice_date']}")
    print(f"  - Amount: {invoice_data['total_amount']}")
    print(f"  - Items: {len(invoice_data['items'])}")
    
    result = evaluator.evaluate_with_category(filename, invoice_data)
    
    print(f"\nEvaluation Result:")
    print(f"  - Category: {result['category']}")
    print(f"  - Category Found: {result['category_found']}")
    print(f"  - Decision: {result['decision']}")
    print(f"  - Reasons: {', '.join(result['reasons'])}")
    print(f"  - Criteria Applied: {result['criteria_applied']}")
    
    print(f"\n✓ Full workflow test completed!")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("APPROVAL EVALUATOR TEST SUITE")
    print("="*60)
    
    try:
        test_category_extraction()
        test_invoice_evaluation()
        test_full_workflow()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED!")
        print("="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

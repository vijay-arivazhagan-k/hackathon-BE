"""
Test script for TinyLlama-based approval evaluation
"""
import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services'))

from approval_evaluator import ApprovalEvaluator

def test_tinyllama_approval():
    """Test TinyLlama approval evaluation with sample invoice data"""
    
    print("="*80)
    print("Testing TinyLlama Approval Evaluator")
    print("="*80)
    
    # Initialize evaluator
    print("\n1. Initializing ApprovalEvaluator (this will load TinyLlama model)...")
    try:
        evaluator = ApprovalEvaluator()
        print("✓ Evaluator initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize evaluator: {str(e)}")
        return
    
    # Sample invoice data
    sample_invoice = {
        'total_amount': 1500.00,
        'items': [
            {'description': 'Laptop', 'amount': 1200.00},
            {'description': 'Mouse', 'amount': 50.00},
            {'description': 'Keyboard', 'amount': 250.00}
        ],
        'invoice_number': 'INV-2025-001',
        'invoice_date': '2025-11-06'
    }
    
    # Sample approval criteria
    approval_criteria = """
    Approval Rules:
    - Invoices under $2000 with less than 5 items can be auto-approved
    - Invoices over $2000 require manager approval
    - Technology purchases over $1000 require additional review
    """
    
    print("\n2. Sample Invoice Data:")
    print(f"   Amount: ${sample_invoice['total_amount']:.2f}")
    print(f"   Items: {len(sample_invoice['items'])}")
    print(f"   Invoice #: {sample_invoice['invoice_number']}")
    
    print("\n3. Approval Criteria:")
    print(approval_criteria)
    
    print("\n4. Evaluating with TinyLlama...")
    try:
        result = evaluator.evaluate_invoice(sample_invoice, approval_criteria)
        
        print("\n" + "="*80)
        print("EVALUATION RESULT")
        print("="*80)
        print(f"Decision: {result['decision']}")
        print(f"Reasons:")
        for reason in result['reasons']:
            print(f"  - {reason}")
        print("="*80)
        
    except Exception as e:
        print(f"✗ Evaluation failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test with category workflow
    print("\n5. Testing complete workflow with filename category extraction...")
    try:
        filename = "INV_Technology_2025.pdf"
        result = evaluator.evaluate_with_category(filename, sample_invoice)
        
        print("\n" + "="*80)
        print("CATEGORY-BASED EVALUATION RESULT")
        print("="*80)
        print(f"Filename: {filename}")
        print(f"Extracted Category: {result['category']}")
        print(f"Decision: {result['decision']}")
        print(f"Reasons:")
        for reason in result['reasons']:
            print(f"  - {reason}")
        print("="*80)
        
    except Exception as e:
        print(f"✗ Category evaluation failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_tinyllama_approval()

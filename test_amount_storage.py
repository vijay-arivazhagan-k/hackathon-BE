from services.request_service import RequestService

def test_amount_extraction_and_storage_from_invoice_and_approval():
    service = RequestService()
    invoice_data = {
        'invoice_number': 'INV-TEST-001',
        'invoice_date': '2025-11-07',
        'total_price': '$1,234.50',  # source string
        'items': [{'item_name': 'Widget', 'item_price': '$100.00'}],
        'approval_info': {'status': 'approved', 'total_amount': 1234.50, 'item_count': 1, 'reasons': []},
    }
    req = service.create_request_from_invoice(
        user_id='tester@example.com',
        invoice_data=invoice_data,
        approval_status='Approved'
    )
    assert req.TOTAL_AMOUNT == 1234.50, f"Expected 1234.50 stored, got {req.TOTAL_AMOUNT}"

def test_amount_fallback_total_price_only():
    service = RequestService()
    invoice_data = {
        'invoice_number': 'INV-TEST-002',
        'invoice_date': '2025-11-07',
        'total_price': '$2,001.75',  # should parse to 2001.75
        'items': [],
        'approval_info': {'status': 'pending', 'item_count': 0, 'reasons': []},
    }
    req = service.create_request_from_invoice(
        user_id='tester@example.com',
        invoice_data=invoice_data,
        approval_status='Pending'
    )
    assert req.TOTAL_AMOUNT == 2001.75, f"Expected 2001.75 stored from total_price, got {req.TOTAL_AMOUNT}"

def test_amount_when_missing_defaults_zero():
    service = RequestService()
    invoice_data = {
        'invoice_number': 'INV-TEST-003',
        'invoice_date': '2025-11-07',
        # no total_amount / total_price / approval_info
    }
    req = service.create_request_from_invoice(
        user_id='tester@example.com',
        invoice_data=invoice_data,
        approval_status='Pending'
    )
    assert req.TOTAL_AMOUNT == 0.0, f"Expected 0.0 stored when no amount sources, got {req.TOTAL_AMOUNT}"

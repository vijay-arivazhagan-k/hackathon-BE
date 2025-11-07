import datetime
from services.request_service import RequestService


def test_creation_date_filter_uses_created_on_not_invoice_date():
    service = RequestService()
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    # Create requests with an old invoice_date that should be ignored by filtering logic
    old_invoice_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    for i in range(3):
        invoice_data = {
            'total_amount': 100 + i,
            'invoice_number': f'INV-{i}',
            'category_name': 'General',
            'invoice_date': old_invoice_date  # Should not exclude these when filtering by today's created_on
        }
        service.create_request_from_invoice(user_id='user1', invoice_data=invoice_data)

    # Filter by today (CREATED_ON); should return the 3 created today despite old invoice_date
    items, total = service.list_requests(page=1, page_size=10, start_date=today, end_date=today)
    assert total >= 3, f"Expected at least 3 requests filtered by CREATED_ON, got {total}"
    assert len(items) >= 3, f"Expected at least 3 items returned, got {len(items)}"

    # End date before today should exclude them
    past = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime('%Y-%m-%d')
    items_past, total_past = service.list_requests(page=1, page_size=10, end_date=past)
    assert total_past == 0, f"Expected 0 items when end_date before CREATED_ON; got {total_past}"

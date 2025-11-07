def test_export_with_numeric_category_id(tmp_path):
    service = RequestService()
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    # Create a category via repository to get numeric ID
    from database_categories import CategoryRepository
    cat_repo = CategoryRepository()
    cat = cat_repo.create_category('Travel', 'Travel related', 5000)

    # Create requests using the category NAME (how data is stored)
    for i in range(2):
        invoice_data = {
            'total_amount': 250 + i,
            'invoice_number': f'TRV-{i}',
            'category_name': cat.CATEGORYNAME,  # Stored as name
            'invoice_date': today
        }
        service.create_request_from_invoice(user_id='user2', invoice_data=invoice_data)

    # Call repository export using numeric ID passed as string (simulating frontend)
    from database import RequestRepository
    repo = RequestRepository()
    rows = repo.get_filtered_requests_for_export(start_date=today, end_date=today, category=str(cat.ID))
    assert len(rows) >= 2, f"Expected >=2 rows for numeric category id export, got {len(rows)}"
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

"""
Test script to demonstrate the simplified JSON output format
"""

import json

# Sample raw output from your test
raw_output = {
    "menu": [
        {"nm": "Photography", "discountprice": "12074", "price": "INVOICE"},
        {"nm": "Invoice date: 7/19/24", "num": "Job Details: Photo Shoot", "price": "Shoot"},
        {"nm": "Bride & Groom Portraits", "unitprice": "$500.00", "cnt": "1", "price": "$500,00"},
        {"nm": "Engagement Photoshop", "unitprice": "$300.00", "cnt": "1", "price": "$300.00"},
    ],
    "total": {
        "total_price": "$2,388.00"
    }
}

def extract_invoice_fields(raw_data):
    """Extract only required fields and sanitize amounts (remove currency symbols)."""
    simplified = {
        "invoice_number": "",
        "invoice_date": "",
        "items": [],
        "total_price": ""
    }

    def _sanitize_amount(val: str) -> str:
        if not isinstance(val, str):
            return ""
        cleaned = val.replace('₹', '').replace('$', '').replace('€', '').replace('£', '').strip()
        if ',' in cleaned and '.' in cleaned:
            cleaned = cleaned.replace(',', '')
        if ',' in cleaned and '.' not in cleaned:
            parts = cleaned.split(',')
            if len(parts) > 1:
                cleaned = parts[0] + '.' + ''.join(parts[1:])
        import re
        match = re.findall(r'\d+(?:\.\d+)?', cleaned)
        return match[0] if match else ''

    # Extract invoice date and number
    menu_items = raw_data.get("menu", [])
    for item in menu_items:
        if isinstance(item, dict):
            item_name = item.get("nm", "")
            if isinstance(item_name, str):
                if "invoice" in item_name.lower() or "inv" in item_name.lower():
                    price_val = item.get("price", "")
                    if isinstance(price_val, str) and any(c.isdigit() for c in price_val):
                        simplified["invoice_number"] = _sanitize_amount(price_val)
                    if "discountprice" in item:
                        simplified["invoice_number"] = _sanitize_amount(str(item.get("discountprice", "")))
                if "date" in item_name.lower() or "/" in item_name:
                    simplified["invoice_date"] = item_name.replace("Invoice date:", "").replace("invoice date:", "").strip()

    # Extract items
    for item in menu_items:
        if isinstance(item, dict):
            item_name = item.get("nm", "")
            item_price = item.get("price", "")
            if isinstance(item_name, str) and item_name and \
               "invoice" not in item_name.lower() and \
               "date:" not in item_name.lower() and \
               "street" not in item_name.lower() and \
               "phone:" not in item_name.lower():
                if isinstance(item_price, str):
                    sanitized = _sanitize_amount(item_price)
                    if sanitized:
                        simplified["items"].append({
                            "item_name": item_name,
                            "item_price": sanitized
                        })

    # Total price
    total_data = raw_data.get("total", {})
    if isinstance(total_data, dict):
        simplified["total_price"] = _sanitize_amount(total_data.get("total_price", ""))
    return simplified

# Test the extraction
result = extract_invoice_fields(raw_output)
print(json.dumps(result, indent=2))

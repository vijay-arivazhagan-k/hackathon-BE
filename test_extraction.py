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
    """Extract only the required fields from raw invoice data."""
    simplified = {
        "invoice_number": "",
        "invoice_date": "",
        "items": [],
        "total_price": ""
    }
    
    # Extract invoice date and number from menu items
    menu_items = raw_data.get("menu", [])
    
    for item in menu_items:
        if isinstance(item, dict):
            item_name = item.get("nm", "")
            
            # Check for invoice number
            if isinstance(item_name, str):
                if "invoice" in item_name.lower() or "inv" in item_name.lower():
                    if "price" in item and isinstance(item.get("price"), str):
                        price_val = item.get("price", "")
                        if any(c.isdigit() for c in price_val) and "invoice" not in price_val.lower():
                            simplified["invoice_number"] = price_val
                    if "discountprice" in item:
                        simplified["invoice_number"] = str(item.get("discountprice", ""))
                
                # Check for date
                if "date" in item_name.lower() or "/" in item_name:
                    simplified["invoice_date"] = item_name.replace("Invoice date:", "").replace("invoice date:", "").strip()
    
    # Extract items with names and prices
    for item in menu_items:
        if isinstance(item, dict):
            item_name = item.get("nm", "")
            item_price = item.get("price", "")
            
            # Skip items that are likely metadata
            if isinstance(item_name, str) and item_name and \
               "invoice" not in item_name.lower() and \
               "date:" not in item_name.lower() and \
               "street" not in item_name.lower() and \
               "phone:" not in item_name.lower():
                
                # Only add if we have a valid price
                if item_price and isinstance(item_price, str) and "$" in item_price:
                    simplified["items"].append({
                        "item_name": item_name,
                        "item_price": item_price
                    })
    
    # Extract total price
    total_data = raw_data.get("total", {})
    if isinstance(total_data, dict):
        simplified["total_price"] = total_data.get("total_price", "")
    
    return simplified

# Test the extraction
result = extract_invoice_fields(raw_output)
print(json.dumps(result, indent=2))

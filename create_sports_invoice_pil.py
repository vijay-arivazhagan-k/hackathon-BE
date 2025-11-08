"""
Generate Sports Invoice PNG using PIL/Pillow
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_sports_invoice():
    # Create image with white background
    width, height = 800, 1000
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Try to use Arial, fallback to default
    try:
        font_regular = ImageFont.truetype("arial.ttf", 13)
        font_bold = ImageFont.truetype("arialbd.ttf", 13)
        font_large = ImageFont.truetype("arialbd.ttf", 36)
        font_medium = ImageFont.truetype("arialbd.ttf", 28)
        font_small_bold = ImageFont.truetype("arialbd.ttf", 14)
    except:
        font_regular = ImageFont.load_default()
        font_bold = ImageFont.load_default()
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small_bold = ImageFont.load_default()
    
    y_pos = 40
    
    # Draw logo box (black rectangle with emoji)
    draw.rectangle([40, y_pos, 120, y_pos + 80], fill='black')
    draw.text((65, y_pos + 20), "⚽", fill='white', font=font_large)
    
    # Company name
    draw.text((140, y_pos + 10), "ABC Sports", fill='black', font=font_medium)
    draw.text((140, y_pos + 45), "Invoice", fill='black', font=font_medium)
    
    # Invoice title (right side)
    draw.text((600, y_pos), "INVOICE", fill='black', font=font_large)
    draw.text((500, y_pos + 50), "Invoice #: 12074", fill='black', font=font_regular)
    draw.text((460, y_pos + 80), "Invoice date: 7/19/24", fill='black', font=font_regular)
    draw.text((450, y_pos + 95), "Job Details: Sports Equipment", fill='black', font=font_regular)
    
    y_pos = 180
    
    # Company info (left)
    company_info = [
        "123 Street Name",
        "Denver, CO 80205",
        "P: 555-555-5555",
        "email@samplebusiness.com"
    ]
    for line in company_info:
        draw.text((40, y_pos), line, fill='black', font=font_regular)
        y_pos += 20
    
    # Bill to (right)
    y_pos = 180
    bill_to_info = [
        "Bill to: Customer Name",
        "Address: 123 Street Name",
        "         Denver, CO 80205",
        "Phone: 555-555-5555"
    ]
    for line in bill_to_info:
        draw.text((500, y_pos), line, fill='black', font=font_regular)
        y_pos += 20
    
    # Table header
    y_pos = 300
    draw.rectangle([40, y_pos, 760, y_pos + 35], fill='black')
    draw.text((50, y_pos + 10), "Description", fill='white', font=font_bold)
    draw.text((350, y_pos + 10), "Qty", fill='white', font=font_bold)
    draw.text((420, y_pos + 10), "Unit price", fill='white', font=font_bold)
    draw.text((550, y_pos + 10), "Discount", fill='white', font=font_bold)
    draw.text((690, y_pos + 10), "Price", fill='white', font=font_bold)
    
    y_pos += 35
    
    # Table rows
    items = [
        ("Cricket Bat Professional", "1", "1,500.00", "", "1,500.00"),
        ("Cricket Ball Set (6 pcs)", "1", "500.00", "", "500.00"),
        ("Batting Gloves Premium", "1", "300.00", "", "300.00"),
        ("", "", "", "", "0.00"),
        ("", "", "", "", "0.00"),
        ("", "", "", "", "0.00"),
        ("", "", "", "", "0.00"),
    ]
    
    for item in items:
        draw.line([(40, y_pos), (760, y_pos)], fill='#eeeeee', width=1)
        draw.text((50, y_pos + 10), item[0], fill='black', font=font_regular)
        draw.text((360, y_pos + 10), item[1], fill='black', font=font_regular)
        draw.text((450, y_pos + 10), item[2], fill='black', font=font_regular)
        draw.text((560, y_pos + 10), item[3], fill='black', font=font_regular)
        draw.text((690, y_pos + 10), item[4], fill='black', font=font_regular)
        y_pos += 35
    
    # Totals section
    y_pos += 20
    totals = [
        ("Invoice Subtotal", "2,300.00"),
        ("Tax Rate", "6.00%"),
        ("Sales Tax", "138.00"),
        ("Deposit Received", "50.00"),
    ]
    
    for label, value in totals:
        draw.text((460, y_pos), label, fill='black', font=font_regular)
        draw.text((690, y_pos), value, fill='black', font=font_regular)
        y_pos += 25
    
    # Total line
    draw.line([(460, y_pos), (760, y_pos)], fill='black', width=2)
    y_pos += 10
    draw.text((460, y_pos), "TOTAL", fill='black', font=font_small_bold)
    draw.text((690, y_pos), "2,388.00", fill='black', font=font_small_bold)
    
    # Footer
    y_pos = 850
    draw.text((200, y_pos), "Please make all checks payable to ABC Sports.", 
              fill='black', font=font_regular)
    draw.text((220, y_pos + 20), "email@samplebusiness.com | www.samplebusiness123.com", 
              fill='black', font=font_regular)
    
    # Save the image
    output_path = os.path.join(os.path.dirname(__file__), 'sports_invoice.png')
    img.save(output_path, 'PNG', quality=100, dpi=(300, 300))
    
    print(f"✓ Sports invoice generated successfully!")
    print(f"✓ File saved at: {output_path}")
    print(f"✓ File size: {os.path.getsize(output_path)} bytes")
    
    return output_path

if __name__ == '__main__':
    create_sports_invoice()

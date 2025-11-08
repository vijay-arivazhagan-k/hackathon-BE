"""
Generate Sports Invoice PNG from HTML
"""
import os
from pathlib import Path

try:
    # Try using selenium with Chrome for better quality
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from PIL import Image
    import time
    
    def generate_invoice_png():
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=800,1000')
        chrome_options.add_argument('--force-device-scale-factor=2')  # Higher DPI
        
        # Get the HTML file path
        html_file = Path(__file__).parent / 'create_sports_invoice.html'
        html_url = f'file:///{html_file.absolute().as_posix()}'
        
        # Initialize driver
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Load the HTML
            driver.get(html_url)
            time.sleep(2)  # Wait for rendering
            
            # Take screenshot
            output_file = Path(__file__).parent / 'sports_invoice.png'
            driver.save_screenshot(str(output_file))
            
            print(f"✓ Invoice generated successfully: {output_file}")
            print(f"✓ File location: {output_file.absolute()}")
            
        finally:
            driver.quit()
            
    if __name__ == '__main__':
        generate_invoice_png()
        
except ImportError:
    print("Selenium not available, trying alternative method...")
    
    # Alternative method using imgkit if available
    try:
        import imgkit
        from pathlib import Path
        
        html_file = Path(__file__).parent / 'create_sports_invoice.html'
        output_file = Path(__file__).parent / 'sports_invoice.png'
        
        options = {
            'format': 'png',
            'width': 800,
            'height': 1000,
            'quality': 100,
            'enable-local-file-access': None
        }
        
        imgkit.from_file(str(html_file), str(output_file), options=options)
        print(f"✓ Invoice generated successfully: {output_file}")
        
    except ImportError:
        print("\n" + "="*60)
        print("ALTERNATIVE METHOD:")
        print("="*60)
        print("\nPlease use one of these methods to generate the PNG:\n")
        print("Method 1: Open the HTML file in browser and save as PNG")
        print("  1. Open: create_sports_invoice.html in Chrome")
        print("  2. Right-click -> Print or Ctrl+P")
        print("  3. Destination: Save as PDF")
        print("  4. Convert PDF to PNG using online tool\n")
        print("Method 2: Install required packages")
        print("  pip install selenium pillow")
        print("  Then run this script again\n")
        print("="*60)

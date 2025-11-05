"""
Example client for Invoice Processing REST API
Demonstrates how to call the API from Python
"""

import requests
import json


class InvoiceAPIClient:
    """Client for Invoice Processing API."""
    
    def __init__(self, base_url="http://localhost:5000"):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the API server
        """
        self.base_url = base_url
    
    def health_check(self):
        """Check if the API is healthy."""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def process_invoice_file(self, file_path):
        """
        Process a single invoice file.
        
        Args:
            file_path: Path to the invoice image file
            
        Returns:
            JSON response with extracted data
        """
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{self.base_url}/api/process-invoice",
                files=files
            )
        return response.json()
    
    def process_invoice_url(self, image_url):
        """
        Process an invoice from a URL.
        
        Args:
            image_url: URL of the invoice image
            
        Returns:
            JSON response with extracted data
        """
        data = {'url': image_url}
        response = requests.post(
            f"{self.base_url}/api/process-invoice-url",
            json=data
        )
        return response.json()
    
    def batch_process(self, file_paths):
        """
        Process multiple invoice files.
        
        Args:
            file_paths: List of paths to invoice image files
            
        Returns:
            JSON response with results for each file
        """
        files = [('files', open(fp, 'rb')) for fp in file_paths]
        try:
            response = requests.post(
                f"{self.base_url}/api/batch-process",
                files=files
            )
            return response.json()
        finally:
            # Close all file handles
            for _, f in files:
                f.close()


# Example usage
if __name__ == "__main__":
    # Initialize the client
    client = InvoiceAPIClient("http://localhost:5000")
    
    # 1. Check API health
    print("Checking API health...")
    health = client.health_check()
    print(json.dumps(health, indent=2))
    print()
    
    # 2. Process a single invoice
    print("Processing single invoice...")
    try:
        result = client.process_invoice_file("invoices/test_image.png")
        print(json.dumps(result, indent=2))
    except FileNotFoundError:
        print("File not found. Please place an invoice image in the invoices folder.")
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # 3. Process invoice from URL
    # print("Processing invoice from URL...")
    # result = client.process_invoice_url("https://example.com/invoice.jpg")
    # print(json.dumps(result, indent=2))
    # print()
    
    # 4. Batch process multiple invoices
    # print("Batch processing invoices...")
    # result = client.batch_process([
    #     "invoices/invoice1.jpg",
    #     "invoices/invoice2.jpg"
    # ])
    # print(json.dumps(result, indent=2))

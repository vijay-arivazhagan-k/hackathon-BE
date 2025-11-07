"""
Invoice Processor using Donut Model
Handles invoice image processing and data extraction
"""

import os
import json
import torch
from pathlib import Path
from PIL import Image
from typing import Dict, List, Optional
from transformers import DonutProcessor, VisionEncoderDecoderModel
import pandas as pd
from datetime import datetime
import getpass


class InvoiceProcessor:
    """
    A class to process invoice images using the Donut transformer model.
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the InvoiceProcessor with configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.device = self._get_device()
        self.processor = None
        self.model = None
        self._initialize_model()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def _get_device(self) -> str:
        """Determine the device to use (CUDA, MPS, or CPU)."""
        config_device = self.config.get('device', 'cuda')
        
        if config_device == 'cuda' and torch.cuda.is_available():
            return 'cuda'
        elif config_device == 'mps' and torch.backends.mps.is_available():
            return 'mps'
        else:
            return 'cpu'
    
    def _initialize_model(self):
        """Initialize the Donut model and processor."""
        model_name = self.config['model']['name']
        
        print(f"Loading model: {model_name}")
        print(f"Using device: {self.device}")
        
        self.processor = DonutProcessor.from_pretrained(model_name)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
        
        print("Model loaded successfully!")
    
    def _extract_invoice_fields(self, raw_data: Dict) -> Dict:
        """
        Extract only the required fields from raw invoice data.
        
        Args:
            raw_data: Raw data from model output
            
        Returns:
            Simplified dictionary with only required fields
        """
        simplified = {
            "invoice_number": "",
            "invoice_date": "",
            "items": [],
            "total_price": ""
        }
        
        # Extract invoice date and number from menu items or other fields
        menu_items = raw_data.get("menu", [])
        
        # Try to find invoice number and date
        for item in menu_items:
            if isinstance(item, dict):
                item_name = item.get("nm", "")
                
                # Check for invoice number
                if isinstance(item_name, str):
                    # Look for invoice number in discountprice field first
                    if "discountprice" in item and not simplified["invoice_number"]:
                        disc_price = str(item.get("discountprice", ""))
                        if disc_price and disc_price.isdigit():
                            simplified["invoice_number"] = disc_price
                    
                    # Also check price field if it's in an invoice-related row
                    if ("invoice" in item_name.lower() or "inv" in item_name.lower()) and not simplified["invoice_number"]:
                        if "price" in item and isinstance(item.get("price"), str):
                            price_val = item.get("price", "")
                            if price_val and price_val.isdigit():
                                simplified["invoice_number"] = price_val
                    
                    # Check for date - more flexible matching
                    if not simplified["invoice_date"]:
                        if "date:" in item_name.lower():
                            simplified["invoice_date"] = item_name.split("date:")[-1].strip()
                        elif "/" in item_name and any(c.isdigit() for c in item_name):
                            # If it contains slashes and numbers, likely a date
                            parts = item_name.split()
                            for part in parts:
                                if "/" in part:
                                    simplified["invoice_date"] = part.strip()
                                    break
        
        # Helper to sanitize currency strings (remove symbols, keep digits & dot/comma)
        def _sanitize_amount(val: str) -> str:
            if not isinstance(val, str):
                return ""
            # Replace common currency symbols and spaces
            cleaned = val.replace('₹', '').replace('$', '').replace('€', '').replace('£', '')
            cleaned = cleaned.strip()
            # Normalize comma usage: if both comma and dot exist and comma comes before dot (e.g. 1,234.56) remove commas
            if ',' in cleaned and '.' in cleaned:
                # Likely thousand separators
                cleaned = cleaned.replace(',', '')
            # If only commas and no dots, convert first comma to dot and others remove (e.g. 500,00 -> 500.00)
            if ',' in cleaned and '.' not in cleaned:
                parts = cleaned.split(',')
                if len(parts) > 1:
                    cleaned = parts[0] + '.' + ''.join(parts[1:])
            # Allow only digits and one dot
            import re as _re
            match = _re.findall(r'\d+(?:\.\d+)?', cleaned)
            return match[0] if match else ''

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
                    if item_price and isinstance(item_price, str):
                        sanitized = _sanitize_amount(item_price)
                        if sanitized:
                            simplified["items"].append({
                                "item_name": item_name,
                                "item_price": sanitized
                            })
        
        # Extract total price
        total_data = raw_data.get("total", {})
        if isinstance(total_data, dict):
            raw_total = total_data.get("total_price", "")
            simplified["total_price"] = _sanitize_amount(raw_total) if isinstance(raw_total, str) else raw_total
        
        return simplified
    
    def process_invoice(self, image_path: str) -> Dict:
        """
        Process a single invoice image and extract structured data.
        
        Args:
            image_path: Path to the invoice image
            
        Returns:
            Dictionary containing extracted invoice data
        """
        try:
            # Load and preprocess the image
            image = Image.open(image_path).convert("RGB")
            
            # Prepare inputs
            task_prompt = self.config['model']['task_prompt']
            pixel_values = self.processor(image, return_tensors="pt").pixel_values
            pixel_values = pixel_values.to(self.device)
            
            # Generate output
            decoder_input_ids = self.processor.tokenizer(
                task_prompt, 
                add_special_tokens=False, 
                return_tensors="pt"
            ).input_ids
            decoder_input_ids = decoder_input_ids.to(self.device)
            
            # Generate prediction
            outputs = self.model.generate(
                pixel_values,
                decoder_input_ids=decoder_input_ids,
                max_length=self.config['model']['max_length'],
                early_stopping=True,
                pad_token_id=self.processor.tokenizer.pad_token_id,
                eos_token_id=self.processor.tokenizer.eos_token_id,
                use_cache=True,
                num_beams=1,
                bad_words_ids=[[self.processor.tokenizer.unk_token_id]],
                return_dict_in_generate=True,
            )
            
            # Decode the output
            sequence = self.processor.batch_decode(outputs.sequences)[0]
            sequence = sequence.replace(self.processor.tokenizer.eos_token, "").replace(
                self.processor.tokenizer.pad_token, ""
            )
            sequence = sequence.replace(task_prompt, "")
            
            # Parse the JSON output
            result = self.processor.token2json(sequence)
            
            # Extract only required fields
            simplified_data = self._extract_invoice_fields(result)
            
            return {
                "status": "success",
                "file": os.path.basename(image_path),
                "data": simplified_data
            }
            
        except Exception as e:
            return {
                "status": "error",
                "file": os.path.basename(image_path),
                "error": str(e)
            }
    
    def process_directory(self, input_dir: str, output_dir: Optional[str] = None) -> List[Dict]:
        """
        Process all invoice images in a directory.
        
        Args:
            input_dir: Directory containing invoice images
            output_dir: Directory to save output JSON files (optional)
            
        Returns:
            List of dictionaries containing results for each invoice
        """
        input_path = Path(input_dir)
        if not input_path.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        # Get supported file formats
        supported_formats = self.config['processing']['supported_formats']
        
        # Find all image files
        image_files = []
        for ext in supported_formats:
            if ext != '.pdf':  # Skip PDF for now (requires additional library)
                image_files.extend(input_path.glob(f"*{ext}"))
        
        if not image_files:
            print(f"No supported image files found in {input_dir}")
            return []
        
        print(f"Found {len(image_files)} invoice(s) to process")
        
        results = []
        for idx, image_file in enumerate(image_files, 1):
            print(f"\nProcessing {idx}/{len(image_files)}: {image_file.name}")
            result = self.process_invoice(str(image_file))
            results.append(result)
            
            # Save individual result if output directory is specified
            if output_dir and result['status'] == 'success':
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                
                output_file = output_path / f"{image_file.stem}_output.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"Saved output to: {output_file}")
        
        return results
    
    def save_results(self, results: List[Dict], output_file: str):
        """
        Save processing results to a JSON file.
        
        Args:
            results: List of processing results
            output_file: Path to output JSON file
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Ensure each result includes processed_by if not present
            username = getpass.getuser()
            for r in results:
                if 'processed_by' not in r:
                    r['processed_by'] = username
                if 'user_id' not in r:
                    r['user_id'] = username
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\nAll results saved to: {output_file}")
    
    def check_approval_status(self, invoice_data: Dict) -> Dict:
        """
        Check if invoice meets approval criteria.
        
        Approval Rules:
        1. Number of items must be less than 5
        2. Total amount must be less than 2000
        
        Args:
            invoice_data: Invoice data dictionary
            
        Returns:
            Dictionary with approval status and details
        """
        items = invoice_data.get('items', [])
        total_price_str = invoice_data.get('total_price', '0')
        
        # Extract numeric value from total price (remove $ and commas)
        try:
            total_amount = float(total_price_str.replace('$', '').replace(',', '').strip())
        except (ValueError, AttributeError):
            total_amount = 0
        
        # Check approval criteria
        item_count = len(items)
        items_ok = item_count < 5
        amount_ok = total_amount < 2000
        
        approved = items_ok and amount_ok
        
        # Build reason message
        reasons = []
        if not items_ok:
            reasons.append(f"Item count ({item_count}) >= 5")
        if not amount_ok:
            reasons.append(f"Total amount (${total_amount:.2f}) >= $2000")
        
        return {
            'approved': approved,
            'status': 'approved' if approved else 'pending',
            'item_count': item_count,
            'total_amount': total_amount,
            'reasons': reasons if not approved else ['All approval criteria met']
        }
    
    def export_to_excel(self, invoice_data: Dict, output_file: str, approval_info: Dict = None):
        """
        Export invoice data to Excel file.
        
        Args:
            invoice_data: Invoice data dictionary
            output_file: Path to output Excel file
            approval_info: Optional approval information dictionary
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create Excel writer
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Sheet 1: Invoice Summary
            # Include processed_by / user info if present, otherwise use local username
            username = invoice_data.get('user_id') or getpass.getuser()

            summary_fields = ['Invoice Number', 'Invoice Date', 'Total Price', 'Processing Date', 'Processed By']
            summary_values = [
                invoice_data.get('invoice_number', ''),
                invoice_data.get('invoice_date', ''),
                invoice_data.get('total_price', ''),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                username
            ]
            
            # Add approval information if provided
            if approval_info:
                summary_fields.extend(['Approval Status', 'Item Count', 'Total Amount', 'Approval Notes'])
                summary_values.extend([
                    approval_info.get('status', '').upper(),
                    str(approval_info.get('item_count', '')),
                    f"${approval_info.get('total_amount', 0):.2f}",
                    '; '.join(approval_info.get('reasons', []))
                ])
            
            summary_data = {
                'Field': summary_fields,
                'Value': summary_values
            }
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Summary', index=False)
            
            # Sheet 2: Line Items
            items = invoice_data.get('items', [])
            if items:
                df_items = pd.DataFrame(items)
                df_items.to_excel(writer, sheet_name='Items', index=False)
            else:
                # Create empty items sheet
                df_items = pd.DataFrame(columns=['item_name', 'item_price'])
                df_items.to_excel(writer, sheet_name='Items', index=False)
            
            # Auto-adjust column widths
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"Excel file saved to: {output_file}")

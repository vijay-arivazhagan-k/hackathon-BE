"""
Flask REST API for Invoice Processing Service
Exposes endpoints for processing invoice images using Donut model
"""

import os
import sys
import time
import threading
import shutil
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path
import traceback
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from invoice_processor import InvoiceProcessor
from teams_notifier import TeamsNotifier

# Import request service for database operations
from services.request_service import RequestService

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Folder paths for automatic processing
# Explicitly watch the Incoming subfolder so the watcher monitors new files placed into
# the 'Incoming' directory. This fixes cases where the parent folder was created but the
# actual incoming folder used by users was 'Incoming' (case-sensitive on some setups).
INCOMING_FOLDER = r"C:\Users\GBS09515\OneDrive - Sella\Documents\Invoices\Incoming"
APPROVED_FOLDER = r"C:\Users\gbs09515\OneDrive - Sella\Documents\Invoices\Approved"
PENDING_FOLDER = r"C:\Users\gbs09515\OneDrive - Sella\Documents\Invoices\Pending"
REJECTED_FOLDER = r"C:\Users\gbs09515\OneDrive - Sella\Documents\Invoices\Rejected"

# Teams webhook configuration
TEAMS_WEBHOOK_URL = "https://gruppobancasella.webhook.office.com/webhookb2/a1ef1298-76e7-420d-94e6-e2a1d7a36f3c@91b02abd-daec-432a-8ee4-b5137910aca6/IncomingWebhook/c43396340ac842aea42d0dea3645ae3e/a8c94719-1818-4f8b-b688-a152204a2036/V2FiNcJLFoh_Pq43yFzmDJJQM_TiXMq-Okh9y8VE7mIIs1"
API_BASE_URL = "http://localhost:5000"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# Ensure the Incoming folder exists (watcher depends on this exact path)
os.makedirs(INCOMING_FOLDER, exist_ok=True)
os.makedirs(APPROVED_FOLDER, exist_ok=True)
os.makedirs(PENDING_FOLDER, exist_ok=True)
os.makedirs(REJECTED_FOLDER, exist_ok=True)

# Initialize the invoice processor (singleton)
processor = None
file_observer = None
teams_notifier = None
request_service = None


def get_processor():
    """Get or initialize the invoice processor."""
    global processor
    if processor is None:
        print("Initializing Invoice Processor...")
        processor = InvoiceProcessor(config_path='config.json')
        print("Processor initialized successfully!")
    return processor


def get_teams_notifier():
    """Get or initialize the Teams notifier."""
    global teams_notifier
    if teams_notifier is None:
        teams_notifier = TeamsNotifier(TEAMS_WEBHOOK_URL, API_BASE_URL)
    return teams_notifier


def get_request_service():
    """Get or initialize the request service."""
    global request_service
    if request_service is None:
        request_service = RequestService()
    return request_service


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class InvoiceFileHandler(FileSystemEventHandler):
    """Handles new invoice files in the incoming folder."""
    
    def __init__(self, processor):
        super().__init__()
        self.processor = processor
        self.processing = set()  # Track files being processed
    
    def on_created(self, event):
        """Called when a new file is created in the watched folder."""
        if event.is_directory:
            return
        
        filepath = event.src_path
        filename = os.path.basename(filepath)
        
        # Check if file is an allowed type
        if not allowed_file(filename):
            print(f"Skipping non-invoice file: {filename}")
            return
        
        # Avoid processing the same file multiple times
        if filepath in self.processing:
            return
        
        # Wait a bit to ensure file is completely written
        time.sleep(2)
        
        # Check if file still exists (might have been moved by another process)
        if not os.path.exists(filepath):
            return
        
        self.processing.add(filepath)
        
        try:
            print(f"\n{'='*60}")
            print(f"New invoice detected: {filename}")
            print(f"{'='*60}")
            
            # Process the invoice
            result = self.processor.process_invoice(filepath)
            
            if result['status'] == 'success':
                invoice_data = result['data']
                base_name = Path(filename).stem
                
                # Check approval status
                approval_info = self.processor.check_approval_status(invoice_data)
                approval_status = approval_info['status']
                
                # Determine output folder based on approval status
                output_folder = APPROVED_FOLDER if approval_status == 'approved' else PENDING_FOLDER
                
                # Generate output filenames
                json_output = os.path.join(output_folder, f"{base_name}_output.json")
                excel_output = os.path.join(output_folder, f"{base_name}_output.xlsx")
                output_image = os.path.join(output_folder, filename)
                
                # Prepare enhanced JSON output with approval info
                enhanced_data = {
                    **invoice_data,
                    'approval_status': approval_status,
                    'approval_info': approval_info
                }
                
                # Save JSON output
                with open(json_output, 'w', encoding='utf-8') as f:
                    import json
                    json.dump(enhanced_data, f, indent=2, ensure_ascii=False)
                print(f"✓ JSON saved: {json_output}")
                
                # Create Excel file with approval info
                self.processor.export_to_excel(invoice_data, excel_output, approval_info)
                print(f"✓ Excel saved: {excel_output}")
                
                # Move original image to appropriate folder
                shutil.move(filepath, output_image)
                print(f"✓ Image moved to: {output_image}")
                
                # Display approval status
                print(f"\n📋 Approval Status: {approval_status.upper()}")
                print(f"   Items: {approval_info['item_count']} | Amount: ${approval_info['total_amount']:.2f}")
                print(f"   Reason: {'; '.join(approval_info['reasons'])}")
                
                # Send Teams notification for pending invoices
                if approval_status == 'pending':
                    print(f"\n📨 Sending Teams notification for approval...")
                    notifier = get_teams_notifier()
                    notifier.send_approval_request(
                        invoice_data, 
                        approval_info, 
                        filename, 
                        output_image
                    )
                
                # Insert request into database after successful processing
                try:
                    req_service = get_request_service()
                    # Extract category from filename (before file extension)
                    category_name = base_name.split('_')[0] if '_' in base_name else 'General'
                    enhanced_data['category_name'] = category_name
                    
                    # Determine user ID (could be extracted from filename or default)
                    user_id = enhanced_data.get('user_id', 'SYSTEM')
                    
                    # Create request in database
                    db_request = req_service.create_request_from_invoice(
                        user_id=user_id,
                        invoice_data=enhanced_data,
                        approval_status=approval_status.title(),  # Convert to title case
                        created_by='AI'
                    )
                    
                    print(f"✓ Request created in database: ID {db_request.ID}")
                    
                except Exception as db_error:
                    print(f"⚠️ Warning: Failed to save request to database: {str(db_error)}")
                    # Don't fail the entire process if database insert fails
                
                print(f"✓ Successfully processed: {filename}")
                print(f"{'='*60}\n")
            else:
                print(f"✗ Error processing {filename}: {result.get('error', 'Unknown error')}")
                # Move failed file to pending with error marker
                error_filename = f"ERROR_{filename}"
                shutil.move(filepath, os.path.join(PENDING_FOLDER, error_filename))
                print(f"Moved failed file to: {error_filename}")
        
        except Exception as e:
            print(f"✗ Exception processing {filename}: {str(e)}")
            traceback.print_exc()
        
        finally:
            self.processing.discard(filepath)


def start_file_watcher():
    """Start watching the incoming folder for new invoices."""
    global file_observer
    
    if file_observer is not None:
        return
    
    proc = get_processor()
    event_handler = InvoiceFileHandler(proc)
    file_observer = Observer()
    file_observer.schedule(event_handler, INCOMING_FOLDER, recursive=False)
    file_observer.start()
    
    print(f"\n{'='*60}")
    print("File Watcher Started")
    print(f"{'='*60}")
    print(f"Watching:  {INCOMING_FOLDER}")
    print(f"Approved:  {APPROVED_FOLDER}")
    print(f"Pending:   {PENDING_FOLDER}")
    print(f"{'='*60}\n")


def stop_file_watcher():
    """Stop the file watcher."""
    global file_observer
    
    if file_observer is not None:
        file_observer.stop()
        file_observer.join()
        file_observer = None
        print("\nFile watcher stopped.")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Invoice Processing API',
        'version': '1.0.0'
    }), 200


@app.route('/api/process-invoice', methods=['POST'])
def process_invoice():
    """
    Process a single invoice image.
    
    Expected: multipart/form-data with 'file' field
    Returns: JSON with extracted invoice data
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No file provided. Please send file as multipart/form-data with key "file"'
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No file selected'
            }), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({
                'status': 'error',
                'message': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Save file securely
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Process the invoice
            proc = get_processor()
            result = proc.process_invoice(filepath)
            
            # Clean up uploaded file
            os.remove(filepath)
            
            if result['status'] == 'success':
                return jsonify({
                    'status': 'success',
                    'data': result['data']
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': result.get('error', 'Processing failed')
                }), 500
                
        except Exception as e:
            # Clean up uploaded file in case of error
            if os.path.exists(filepath):
                os.remove(filepath)
            raise e
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/process-invoice-url', methods=['POST'])
def process_invoice_url():
    """
    Process an invoice from a URL.
    
    Expected: JSON with 'url' field
    Returns: JSON with extracted invoice data
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'status': 'error',
                'message': 'No URL provided. Please send JSON with "url" field'
            }), 400
        
        url = data['url']
        
        # Download image from URL
        import requests
        from io import BytesIO
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Save to temporary file
        filename = f"temp_{os.urandom(8).hex()}.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        try:
            # Process the invoice
            proc = get_processor()
            result = proc.process_invoice(filepath)
            
            # Clean up temporary file
            os.remove(filepath)
            
            if result['status'] == 'success':
                return jsonify({
                    'status': 'success',
                    'data': result['data']
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': result.get('error', 'Processing failed')
                }), 500
                
        except Exception as e:
            # Clean up temporary file in case of error
            if os.path.exists(filepath):
                os.remove(filepath)
            raise e
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/batch-process', methods=['POST'])
def batch_process():
    """
    Process multiple invoice images.
    
    Expected: multipart/form-data with multiple 'files' fields
    Returns: JSON array with results for each invoice
    """
    try:
        # Check if files are present
        if 'files' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No files provided. Please send files as multipart/form-data with key "files"'
            }), 400
        
        files = request.files.getlist('files')
        
        if not files or len(files) == 0:
            return jsonify({
                'status': 'error',
                'message': 'No files selected'
            }), 400
        
        results = []
        proc = get_processor()
        
        for file in files:
            if file.filename == '':
                continue
            
            if not allowed_file(file.filename):
                results.append({
                    'filename': file.filename,
                    'status': 'error',
                    'message': 'File type not allowed'
                })
                continue
            
            # Save file securely
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                # Process the invoice
                result = proc.process_invoice(filepath)
                results.append({
                    'filename': file.filename,
                    'status': result['status'],
                    'data': result.get('data') if result['status'] == 'success' else None,
                    'error': result.get('error') if result['status'] == 'error' else None
                })
                
            except Exception as e:
                results.append({
                    'filename': file.filename,
                    'status': 'error',
                    'message': str(e)
                })
            
            finally:
                # Clean up uploaded file
                if os.path.exists(filepath):
                    os.remove(filepath)
        
        return jsonify({
            'status': 'success',
            'total': len(results),
            'results': results
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/watcher/status', methods=['GET'])
def watcher_status():
    """Get file watcher status."""
    global file_observer
    return jsonify({
        'status': 'running' if file_observer and file_observer.is_alive() else 'stopped',
        'incoming_folder': INCOMING_FOLDER,
        'approved_folder': APPROVED_FOLDER,
        'pending_folder': PENDING_FOLDER,
        'rejected_folder': REJECTED_FOLDER,
        'teams_integration': 'enabled',
        'teams_webhook_configured': bool(TEAMS_WEBHOOK_URL)
    }), 200


@app.route('/api/watcher/start', methods=['POST'])
def start_watcher():
    """Start the file watcher."""
    try:
        start_file_watcher()
        return jsonify({
            'status': 'success',
            'message': 'File watcher started'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/watcher/stop', methods=['POST'])
def stop_watcher():
    """Stop the file watcher."""
    try:
        stop_file_watcher()
        return jsonify({
            'status': 'success',
            'message': 'File watcher stopped'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/invoice/view/<path:filename>', methods=['GET'])
def view_invoice(filename):
    """
    View/download an invoice file from the pending folder.
    """
    try:
        from urllib.parse import unquote
        filename = unquote(filename)
        
        # Check in pending folder
        file_path = os.path.join(PENDING_FOLDER, filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                'status': 'error',
                'message': 'Invoice file not found'
            }), 404
        
        from flask import send_file
        return send_file(file_path, as_attachment=False)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/invoice/approve/<path:filename>', methods=['GET', 'POST'])
def approve_invoice(filename):
    """
    Approve an invoice - move from Pending to Approved folder.
    """
    try:
        from urllib.parse import unquote
        import json as json_module
        
        filename = unquote(filename)
        
        # Find all related files in pending folder
        base_name = Path(filename).stem
        pending_image = os.path.join(PENDING_FOLDER, filename)
        pending_json = os.path.join(PENDING_FOLDER, f"{base_name}_output.json")
        pending_excel = os.path.join(PENDING_FOLDER, f"{base_name}_output.xlsx")
        
        # Target paths in approved folder
        approved_image = os.path.join(APPROVED_FOLDER, filename)
        approved_json = os.path.join(APPROVED_FOLDER, f"{base_name}_output.json")
        approved_excel = os.path.join(APPROVED_FOLDER, f"{base_name}_output.xlsx")
        
        if not os.path.exists(pending_image):
            return jsonify({
                'status': 'error',
                'message': 'Invoice not found in pending folder'
            }), 404
        
        # Read invoice number from JSON for notification
        invoice_number = "N/A"
        if os.path.exists(pending_json):
            with open(pending_json, 'r', encoding='utf-8') as f:
                data = json_module.load(f)
                invoice_number = data.get('invoice_number', 'N/A')
                # Update approval status in JSON
                data['approval_status'] = 'approved'
                data['manually_approved'] = True
            
            # Save updated JSON to approved folder
            with open(approved_json, 'w', encoding='utf-8') as f:
                json_module.dump(data, f, indent=2, ensure_ascii=False)
            os.remove(pending_json)
        
        # Move files to approved folder
        shutil.move(pending_image, approved_image)
        if os.path.exists(pending_excel):
            shutil.move(pending_excel, approved_excel)
        
        print(f"✅ Invoice {filename} approved and moved to Approved folder")
        
        # Send Teams notification
        notifier = get_teams_notifier()
        notifier.send_approval_result(filename, True, invoice_number)
        
        # Return HTML response for browser
        return """
        <html>
        <head>
            <title>Invoice Approved</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f0f0f0; }
                .success { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 500px; margin: 0 auto; }
                h1 { color: #28a745; }
                .checkmark { font-size: 60px; color: #28a745; }
            </style>
        </head>
        <body>
            <div class="success">
                <div class="checkmark">✅</div>
                <h1>Invoice Approved!</h1>
                <p>Invoice <strong>""" + filename + """</strong> has been approved and moved to the Approved folder.</p>
                <p style="color: #666; margin-top: 30px;">You can close this window.</p>
            </div>
        </body>
        </html>
        """, 200
        
    except Exception as e:
        print(f"✗ Error approving invoice: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/invoice/reject/<path:filename>', methods=['GET', 'POST'])
def reject_invoice(filename):
    """
    Reject an invoice - move from Pending to Rejected folder.
    """
    try:
        from urllib.parse import unquote
        import json as json_module
        
        filename = unquote(filename)
        
        # Find all related files in pending folder
        base_name = Path(filename).stem
        pending_image = os.path.join(PENDING_FOLDER, filename)
        pending_json = os.path.join(PENDING_FOLDER, f"{base_name}_output.json")
        pending_excel = os.path.join(PENDING_FOLDER, f"{base_name}_output.xlsx")
        
        # Target paths in rejected folder
        rejected_image = os.path.join(REJECTED_FOLDER, filename)
        rejected_json = os.path.join(REJECTED_FOLDER, f"{base_name}_output.json")
        rejected_excel = os.path.join(REJECTED_FOLDER, f"{base_name}_output.xlsx")
        
        if not os.path.exists(pending_image):
            return jsonify({
                'status': 'error',
                'message': 'Invoice not found in pending folder'
            }), 404
        
        # Read invoice number from JSON for notification
        invoice_number = "N/A"
        if os.path.exists(pending_json):
            with open(pending_json, 'r', encoding='utf-8') as f:
                data = json_module.load(f)
                invoice_number = data.get('invoice_number', 'N/A')
                # Update approval status in JSON
                data['approval_status'] = 'rejected'
                data['manually_rejected'] = True
            
            # Save updated JSON to rejected folder
            with open(rejected_json, 'w', encoding='utf-8') as f:
                json_module.dump(data, f, indent=2, ensure_ascii=False)
            os.remove(pending_json)
        
        # Move files to rejected folder
        shutil.move(pending_image, rejected_image)
        if os.path.exists(pending_excel):
            shutil.move(pending_excel, rejected_excel)
        
        print(f"❌ Invoice {filename} rejected and moved to Rejected folder")
        
        # Send Teams notification
        notifier = get_teams_notifier()
        notifier.send_approval_result(filename, False, invoice_number)
        
        # Return HTML response for browser
        return """
        <html>
        <head>
            <title>Invoice Rejected</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f0f0f0; }
                .rejected { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 500px; margin: 0 auto; }
                h1 { color: #dc3545; }
                .cross { font-size: 60px; color: #dc3545; }
            </style>
        </head>
        <body>
            <div class="rejected">
                <div class="cross">❌</div>
                <h1>Invoice Rejected</h1>
                <p>Invoice <strong>""" + filename + """</strong> has been rejected and moved to the Rejected folder.</p>
                <p style="color: #666; margin-top: 30px;">You can close this window.</p>
            </div>
        </body>
        </html>
        """, 200
        
    except Exception as e:
        print(f"✗ Error rejecting invoice: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/', methods=['GET'])
def index():
    """API documentation endpoint."""
    return jsonify({
        'service': 'Invoice Processing API',
        'version': '1.0.0',
        'file_watcher': {
            'incoming_folder': INCOMING_FOLDER,
            'approved_folder': APPROVED_FOLDER,
            'pending_folder': PENDING_FOLDER,
            'status': 'running' if file_observer and file_observer.is_alive() else 'stopped'
        },
        'approval_rules': {
            'item_count_limit': 5,
            'amount_limit': 2000,
            'description': 'Invoices with <5 items AND <$2000 are auto-approved'
        },
        'endpoints': {
            '/health': {
                'method': 'GET',
                'description': 'Health check endpoint'
            },
            '/api/watcher/status': {
                'method': 'GET',
                'description': 'Get file watcher status'
            },
            '/api/watcher/start': {
                'method': 'POST',
                'description': 'Start the file watcher'
            },
            '/api/watcher/stop': {
                'method': 'POST',
                'description': 'Stop the file watcher'
            },
            '/api/invoice/view/<filename>': {
                'method': 'GET',
                'description': 'View/download invoice image file'
            },
            '/api/invoice/approve/<filename>': {
                'method': 'GET/POST',
                'description': 'Approve a pending invoice (moves to Approved folder)'
            },
            '/api/invoice/reject/<filename>': {
                'method': 'GET/POST',
                'description': 'Reject a pending invoice (moves to Rejected folder)'
            },
            '/api/process-invoice': {
                'method': 'POST',
                'description': 'Process a single invoice image',
                'content_type': 'multipart/form-data',
                'parameters': {
                    'file': 'Invoice image file (jpg, jpeg, png)'
                },
                'example': 'curl -X POST -F "file=@invoice.jpg" http://localhost:5000/api/process-invoice'
            },
            '/api/process-invoice-url': {
                'method': 'POST',
                'description': 'Process an invoice from a URL',
                'content_type': 'application/json',
                'parameters': {
                    'url': 'URL of the invoice image'
                },
                'example': 'curl -X POST -H "Content-Type: application/json" -d \'{"url":"https://example.com/invoice.jpg"}\' http://localhost:5000/api/process-invoice-url'
            },
            '/api/batch-process': {
                'method': 'POST',
                'description': 'Process multiple invoice images',
                'content_type': 'multipart/form-data',
                'parameters': {
                    'files': 'Multiple invoice image files'
                },
                'example': 'curl -X POST -F "files=@invoice1.jpg" -F "files=@invoice2.jpg" http://localhost:5000/api/batch-process'
            }
        }
    }), 200


if __name__ == '__main__':
    print("="*60)
    print("Invoice Processing REST API")
    print("="*60)
    print("\nInitializing service...")
    
    # Pre-load the model
    get_processor()
    
    print("\n" + "="*60)
    print("Server is ready!")
    print("="*60)
    print("\nAPI Endpoints:")
    print("  - Health Check:     GET  http://localhost:5000/health")
    print("  - Process Invoice:  POST http://localhost:5000/api/process-invoice")
    print("  - Process URL:      POST http://localhost:5000/api/process-invoice-url")
    print("  - Batch Process:    POST http://localhost:5000/api/batch-process")
    print("  - Watcher Status:   GET  http://localhost:5000/api/watcher/status")
    print("  - Documentation:    GET  http://localhost:5000/")
    print("\n" + "="*60 + "\n")
    
    # Start the file watcher in a separate thread
    print("Starting automatic file watcher...")
    start_file_watcher()
    
    try:
        # Run the Flask app
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    finally:
        # Cleanup on shutdown
        print("\nShutting down...")
        stop_file_watcher()

# InvoiceAI - Invoice Processing with Donut Model

A Python application that processes invoice images using the Donut (Document Understanding Transformer) model to extract structured data as JSON output.

## Features

- 🔍 Automatic invoice data extraction using state-of-the-art Donut transformer model
- 📄 Processes multiple invoice formats (JPEG, PNG, JPG)
- 🚀 GPU acceleration support (CUDA)
- 📊 Outputs structured JSON data
- 🎯 Easy configuration via JSON config file
- 📁 Batch processing support for multiple invoices
- 🌐 **REST API service** for remote invocation
- 🔌 CORS-enabled for web applications
- 📨 **Microsoft Teams integration** with Adaptive Cards for approvals
- ✅ Interactive approve/reject buttons in Teams

## Requirements

- Python 3.11 or above
- CUDA-compatible GPU (optional, but recommended for better performance)

## Installation

1. Install the required dependencies:

```powershell
pip install -r requirements.txt
```

**Note:** First run will download the pre-trained Donut model (~1.5GB), which may take a few minutes depending on your internet connection.

## Project Structure

```
InvoiceAI/
├── src/
│   ├── __init__.py
│   └── invoice_processor.py    # Main invoice processing logic
├── invoices/                    # Input directory for invoice images
├── output/                      # Output directory for JSON results
├── uploads/                     # Temporary upload directory for API
├── config.json                  # Configuration file
├── main.py                      # CLI entry point
├── app.py                       # REST API service
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Configuration

Edit `config.json` to customize the processing behavior:

```json
{
    "model": {
        "name": "naver-clova-ix/donut-base-finetuned-cord-v2",
        "task_prompt": "<s_cord-v2>",
        "max_length": 512
    },
    "processing": {
        "input_path": "./invoices",
        "output_path": "./output",
        "supported_formats": [".jpg", ".jpeg", ".png", ".pdf"]
    },
    "device": "cuda"
}
```

- `device`: Set to "cuda" for GPU, "cpu" for CPU processing

## Usage

### Option 1: Command Line Interface (CLI)

#### Process a Directory of Invoices

Place your invoice images in the `invoices` directory and run:

```powershell
python main.py
```

Or specify custom paths:

```powershell
python main.py --input ./my_invoices --output ./my_output
```

#### Process a Single Invoice

```powershell
python main.py --input invoice.jpg --output ./output --single
```

#### Command Line Arguments

- `--input`: Path to input directory or single invoice image (default: `./invoices`)
- `--output`: Path to output directory for JSON results (default: `./output`)
- `--config`: Path to configuration file (default: `config.json`)
- `--single`: Process a single invoice file instead of a directory

### Option 2: REST API Service with Automatic Processing

#### Starting the API Server

```powershell
python app.py
```

The server will start on `http://localhost:5000` and automatically:
- 📂 Watch `C:\Users\gbs09515\OneDrive - Sella\Documents\Invoices\Incoming` for new invoice images
- 🔄 Process any new invoice files automatically
- ✅ Apply approval rules to categorize invoices
- 📊 Generate Excel files with extracted data and approval status
- 💾 Save JSON output files
- 📁 Route invoices to **Approved** or **Pending** folders based on rules

**Approval Rules (Auto-Applied):**
- ✅ **APPROVED**: Item count < 5 AND Total amount < $2,000
- ⏳ **PENDING**: Item count >= 5 OR Total amount >= $2,000

**Automatic Processing Workflow:**
1. Drop an invoice image into the Incoming folder
2. API automatically detects and processes it
3. Applies approval rules
4. Routes to appropriate folder:
   - **Approved Folder**: Invoices meeting both criteria (< 5 items AND < $2000)
   - **Pending Folder**: Invoices requiring manual review
5. **For Pending Invoices**:
   - 📨 Adaptive Card sent to Microsoft Teams
   - Card shows invoice details with approve/reject buttons
   - Click "View Invoice" to see the original image
   - Click "Approve" → Moves to Approved folder
   - Click "Reject" → Moves to Rejected folder
6. Each folder contains:
   - `{filename}_output.json` - JSON with extracted data and approval status
   - `{filename}_output.xlsx` - Excel file with invoice details and approval info
   - Original invoice image

#### API Endpoints

**1. Health Check**
```bash
GET http://localhost:5000/health
```

**2. File Watcher Status**
```bash
GET http://localhost:5000/api/watcher/status
```

**3. Start/Stop File Watcher**
```bash
POST http://localhost:5000/api/watcher/start
POST http://localhost:5000/api/watcher/stop
```

**4. Process Single Invoice (File Upload)**
```bash
curl -X POST -F "file=@invoice.jpg" http://localhost:5000/api/process-invoice
```

PowerShell example:
```powershell
$uri = "http://localhost:5000/api/process-invoice"
$filePath = "C:\path\to\invoice.jpg"
$fileBytes = [System.IO.File]::ReadAllBytes($filePath)
$fileName = [System.IO.Path]::GetFileName($filePath)
$boundary = [System.Guid]::NewGuid().ToString()
$contentType = "multipart/form-data; boundary=$boundary"

$body = @"
--$boundary
Content-Disposition: form-data; name="file"; filename="$fileName"
Content-Type: image/jpeg

$([System.Text.Encoding]::GetEncoding('iso-8859-1').GetString($fileBytes))
--$boundary--
"@

Invoke-RestMethod -Uri $uri -Method Post -ContentType $contentType -Body $body
```

**5. Process Invoice from URL**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/invoice.jpg"}' \
  http://localhost:5000/api/process-invoice-url
```

PowerShell example:
```powershell
$body = @{
    url = "https://example.com/invoice.jpg"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/process-invoice-url" `
  -Method Post -ContentType "application/json" -Body $body
```

**6. Batch Process Multiple Invoices**
```bash
curl -X POST \
  -F "files=@invoice1.jpg" \
  -F "files=@invoice2.jpg" \
  http://localhost:5000/api/batch-process
```

**7. Manual Approval Actions**
```bash
# Approve an invoice
GET http://localhost:5000/api/invoice/approve/{filename}

# Reject an invoice
GET http://localhost:5000/api/invoice/reject/{filename}

# View invoice image
GET http://localhost:5000/api/invoice/view/{filename}
```

#### API Response Format

Success response:
```json
{
  "status": "success",
  "data": {
    "invoice_number": "12074",
    "invoice_date": "7/19/24",
    "items": [
      {
        "item_name": "Product Name",
        "item_price": "$100.00"
      }
    ],
    "total_price": "$100.00"
  }
}
```

Error response:
```json
{
  "status": "error",
  "message": "Error description"
}
```

## Output Format

The extracted invoice data is returned in a simplified JSON structure:

```json
{
  "invoice_number": "12074",
  "invoice_date": "7/19/24",
  "items": [
    {
      "item_name": "Product Name",
      "item_price": "$100.00"
    }
  ],
  "total_price": "$100.00"
}
```

**Fields:**
- `invoice_number`: The invoice or receipt number
- `invoice_date`: Date of the invoice
- `items`: Array of line items with name and price
- `total_price`: Total amount

### Excel Output Format

Excel files contain two sheets with approval information:

**Summary Sheet:**
| Field | Value |
|-------|-------|
| Invoice Number | 12074 |
| Invoice Date | 7/19/24 |
| Total Price | $100.00 |
| Processing Date | 2025-11-01 14:30:00 |
| Approval Status | APPROVED |
| Item Count | 3 |
| Total Amount | $100.00 |
| Approval Notes | All approval criteria met |

**Items Sheet:**
| item_name | item_price |
|-----------|------------|
| Product Name | $100.00 |

## Example Workflows

### Automatic Processing with Approval Routing (Recommended)
1. **Start the API server**: `python app.py`
2. **Drop invoices**: Copy invoice images to `C:\Users\gbs09515\OneDrive - Sella\Documents\Invoices\Incoming`
3. **Check results**:
   - **Approved invoices** (< 5 items AND < $2000): `...\Invoices\Approved`
   - **Pending invoices** (>= 5 items OR >= $2000): `...\Invoices\Pending`
4. **Review**: Check console for real-time approval status and routing decisions

### Manual CLI Processing

1. **Prepare invoices**: Place invoice images in the `invoices` folder
2. **Run processing**: Execute `python main.py`
3. **Check results**: Find extracted data in the `output` folder
   - Individual results: `{invoice_name}_output.json`
   - Combined results: `all_results.json`

## Approval System

### Automatic Invoice Approval Rules

The system automatically evaluates each processed invoice against the following criteria:

**Approval Criteria (Both must be met):**
1. ✅ Number of line items < 5
2. ✅ Total invoice amount < $2,000

**Decision Logic:**
- **APPROVED**: Invoice meets BOTH criteria → Routed to `Approved` folder
- **PENDING**: Invoice fails ANY criterion → Routed to `Pending` folder

**Example Scenarios:**

| Items | Amount | Status | Reason |
|-------|--------|--------|--------|
| 3 | $1,500 | ✅ APPROVED | Both criteria met |
| 4 | $1,999 | ✅ APPROVED | Both criteria met |
| 5 | $1,800 | ⏳ PENDING | Item count >= 5 |
| 3 | $2,500 | ⏳ PENDING | Amount >= $2000 |
| 6 | $3,000 | ⏳ PENDING | Both criteria exceeded |

**Output Includes:**
- Approval status in JSON and Excel files
- Item count and total amount
- Detailed reason for approval/pending status

### Customizing Approval Rules

To modify approval thresholds, edit `app.py` or `src/invoice_processor.py`:

```python
# In check_approval_status method
items_ok = item_count < 5      # Change the threshold
amount_ok = total_amount < 2000  # Change the amount
```

## Microsoft Teams Integration

### Adaptive Card Notifications

When an invoice is marked as **PENDING**, an Adaptive Card is automatically sent to Microsoft Teams with:

**Card Features:**
- 📋 Invoice details (number, date, amount, item count)
- 📝 List of line items
- ⚠️ Reason for pending status
- 🔘 Three action buttons:
  - **View Invoice** - Opens the invoice image in browser
  - **Approve** - Moves invoice to Approved folder
  - **Reject** - Moves invoice to Rejected folder

**Workflow:**
1. Pending invoice triggers Teams notification
2. Reviewer receives Adaptive Card in Teams channel
3. Reviewer clicks "View Invoice" to see the image
4. Reviewer clicks "Approve" or "Reject"
5. Invoice is automatically moved to appropriate folder
6. Confirmation notification sent back to Teams

**Configuration:**
- Webhook URL is configured in `app.py` (TEAMS_WEBHOOK_URL)
- To change webhook, update the URL in `app.py`

**Example Adaptive Card:**
```
╔══════════════════════════════════════╗
║  ⏳ Invoice Pending Approval         ║
╠══════════════════════════════════════╣
║  Invoice Number: INV-12074          ║
║  Date: 7/19/24                      ║
║  Total Amount: $2,500.00            ║
║  Item Count: 6                      ║
╠══════════════════════════════════════╣
║  Pending Reason:                    ║
║  • Item count (6) >= 5              ║
╠══════════════════════════════════════╣
║  [📎 View Invoice]                  ║
║  [✅ Approve] [❌ Reject]            ║
╚══════════════════════════════════════╝
```

## Model Information

This project uses the pre-trained Donut model fine-tuned on CORD v2 dataset:
- Model: `naver-clova-ix/donut-base-finetuned-cord-v2`
- Task: Document Understanding / Receipt/Invoice OCR
- Architecture: Vision Encoder-Decoder Transformer

## Performance Notes

- **GPU (CUDA)**: Recommended for faster processing (~2-3 seconds per invoice)
- **CPU**: Slower but functional (~10-15 seconds per invoice)
- First run downloads the model (~1.5GB)

## Troubleshooting

### Import Errors
If you encounter import errors when running `main.py`, make sure you're running from the project root directory.

### CUDA Out of Memory
If processing fails with CUDA out of memory error:
1. Set `"device": "cpu"` in `config.json`
2. Or reduce `max_length` in the configuration

### Model Download Issues
If model download fails:
- Check your internet connection
- Ensure you have sufficient disk space (~2GB)
- Try downloading manually using the transformers library

## Python Version Compatibility

This project is compatible with Python 3.11 and above. Ensure you have the correct Python version:

```powershell
python --version
```

## License

This project uses the Donut model which is available under the MIT license.

## Credits

- Donut Model: [NAVER CLOVA](https://github.com/clovaai/donut)
- Transformers Library: [Hugging Face](https://huggingface.co/)

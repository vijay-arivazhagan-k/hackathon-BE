# Invoice Approval System Implementation

## Overview

The invoice approval system has been enhanced to automatically evaluate invoices based on extracted details and category-specific approval criteria. The system now:

1. **Extracts** category name from filename (format: `PREFIX_CATEGORYNAME.pdf`)
2. **Retrieves** approval criteria from the database for matching categories
3. **Evaluates** invoice data against approval rules
4. **Determines** approval status (Approved or Pending)
5. **Updates** the database with the final status

## Key Components

### 1. Approval Evaluator Service
**File:** `services/approval_evaluator.py`

This is the core service that handles the entire approval workflow:

```python
from services.approval_evaluator import ApprovalEvaluator

evaluator = ApprovalEvaluator()

# Complete workflow in one call:
result = evaluator.evaluate_with_category(filename, invoice_data)
# Returns: {
#   'decision': 'Approved' or 'Pending',
#   'reasons': [...],
#   'category': 'CATEGORYNAME',
#   'category_found': True/False,
#   'criteria': 'approval criteria text or None',
#   'criteria_applied': 'description of criteria used'
# }
```

#### Methods:

- **`extract_category_from_filename(filename)`**
  - Parses filename format: `PREFIX_CATEGORYNAME.ext`
  - Returns category name or 'General' if not found
  - Example: `GBS09500_TRAVEL.pdf` → `TRAVEL`

- **`get_category_approval_criteria(category_name)`**
  - Looks up category in database
  - Returns approval criteria text if found
  - Returns `None` if category not in database

- **`evaluate_invoice(invoice_data, approval_criteria)`**
  - Applies approval rules to invoice data
  - Default rules:
    - **Approved**: `item_count < 5` AND `total_amount < $2000`
    - **Pending**: Otherwise
  - Returns decision with reasoning

- **`evaluate_with_category(filename, invoice_data)`**
  - Complete workflow combining all steps
  - Recommended entry point

### 2. Invoice Data Extraction

Invoice data includes:
```python
{
    'invoice_number': 'INV-12345',      # From file extraction
    'invoice_date': '2024-11-05',       # From file extraction
    'total_price': '$1800.00',          # String format from file
    'total_amount': 1800.0,             # Numeric amount
    'items': [                          # Line items
        {'item_name': 'Item 1', 'item_price': '$500'},
        ...
    ]
}
```

### 3. Database Integration

#### Category Service Updates
**File:** `services/category_service.py`

New method added:
```python
def get_category_by_name(self, categoryname: str) -> Optional[Category]:
    """Get category by name (case-insensitive)"""
```

#### Request Status Updates
**Files:** `database.py`, `services/request_service.py`

The `create_request()` method now accepts a `status` parameter:
```python
request = repository.create_request(
    user_id=user_id,
    total_amount=total_amount,
    invoice_date=invoice_date,
    invoice_number=invoice_number,
    category_name=category_name,
    comments=comments,
    approval_type=approval_type,
    created_by=created_by,
    status='Approved'  # or 'Pending'
)
```

### 4. App.py Integration

**Location:** `app.py` - InvoiceFileHandler.on_created() method

The file watcher now uses the evaluator:

```python
# Use approval evaluator
from services.approval_evaluator import ApprovalEvaluator
evaluator = ApprovalEvaluator()
eval_result = evaluator.evaluate_with_category(filename, invoice_data)

# Get the decision
approval_status = eval_result['decision'].lower()  # 'approved' or 'pending'

# Create request with final status
db_request = req_service.create_request_from_invoice(
    user_id=user_id,
    invoice_data=enhanced_data,
    approval_status=approval_status.title(),  # 'Approved' or 'Pending'
    created_by='AI'
)
```

## Workflow

```
┌─────────────────────────────────────────┐
│  Invoice File Detected                  │
│  (e.g., GBS09500_TRAVEL.pdf)            │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Extract invoice details:               │
│  - category_name from filename          │
│  - invoice_number from content          │
│  - invoice_date from content            │
│  - total_amount from content            │
│  - items list from content              │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Look up category in database           │
│  Get approval_criteria if exists        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Evaluate against rules:                │
│  - Amount < $2000?                      │
│  - Item count < 5?                      │
│  → Decision: Approved or Pending        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Create request in DB                   │
│  Status = Approved or Pending           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Move file to appropriate folder:       │
│  - Approved → /Approved                 │
│  - Pending → /Pending (for review)      │
└─────────────────────────────────────────┘
```

## Testing

Run the test suite:

```bash
cd c:\A_CODE\TRUNK\hackathon\InvoiceAI
python test_approval_evaluator.py
```

Test coverage includes:
- ✓ Category extraction from various filename formats
- ✓ Invoice evaluation logic (approved/pending cases)
- ✓ Full workflow end-to-end

## Database Schema

### Categories Table (IV_MA_CATEGORY)
```sql
CATEGORYNAME        VARCHAR(100) NOT NULL
APPROVAL_CRITERIA   TEXT                   -- New approval rules/conditions
MAXIMUMAMOUNT       REAL                   -- Optional amount threshold
```

### Requests Table (IV_TR_REQUESTS)
```sql
CATEGORY_NAME       VARCHAR(100)
CURRENT_STATUS      VARCHAR(25)            -- 'Approved' or 'Pending'
INVOICE_NUMBER      VARCHAR(50)
INVOICE_DATE        DATE
TOTAL_AMOUNT        DECIMAL(10,2)
```

## Example: Setting Up Category Approval Criteria

```python
from services.category_service import CategoryService

service = CategoryService()

# Create category with approval criteria
category = service.create_category(
    categoryname='TRAVEL',
    approval_criteria='Amount < $2000 AND Items < 5',
    maximumamount=2000.0,
    status=True
)
```

## Configuration and Customization

### Modifying Approval Rules

Edit the `evaluate_invoice()` method in `services/approval_evaluator.py`:

```python
def evaluate_invoice(self, invoice_data: Dict, approval_criteria: Optional[str] = None) -> Dict:
    # Modify the logic here
    if item_count < 5 and total_amount < 2000:
        decision = 'Approved'
    else:
        decision = 'Pending'
```

### Adding GenAI Integration

The evaluator is designed to be extended with GenAI:

```python
def evaluate_invoice(self, invoice_data: Dict, approval_criteria: Optional[str] = None) -> Dict:
    # Call external GenAI service
    genai_response = call_genai_api(invoice_data, approval_criteria)
    decision = genai_response['decision']  # Approved or Pending
    reasons = genai_response['reasoning']
    
    return {
        'decision': decision,
        'reasons': reasons,
        'criteria_applied': approval_criteria
    }
```

## Status and Next Steps

✅ **Completed:**
- Category extraction from filename
- Category lookup in database
- Invoice evaluation logic
- Database status updates
- Integration with app.py file watcher
- Test suite with 100% pass rate

⏳ **Optional Enhancements:**
- GenAI integration for intelligent decision-making
- Custom approval criteria per category
- Approval workflow notifications
- Audit trail and approval history
- Performance optimization for batch processing

## Files Modified/Created

| File | Change |
|------|--------|
| `services/approval_evaluator.py` | **NEW** - Core evaluator service |
| `services/category_service.py` | Added `get_category_by_name()` method |
| `database.py` | Added `status` parameter to `create_request()` |
| `services/request_service.py` | Updated to pass status to repository |
| `app.py` | Integrated evaluator into file watcher |
| `test_approval_evaluator.py` | **NEW** - Test suite |


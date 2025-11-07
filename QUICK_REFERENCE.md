# Quick Reference: Invoice Approval System

## What Was Implemented

✅ **Complete invoice approval system** with automatic categorization and decision-making

## The Flow

```
Invoice File → Extract Details → Lookup Category → Evaluate Rules → DB Update → Move File
```

## How It Works

### 1️⃣ Filename Parsing
```
GBS09500_TRAVEL.pdf
       ↓
    Extract: TRAVEL
```

### 2️⃣ Invoice Details
- `invoice_number` - From file content
- `invoice_date` - From file content  
- `total_amount` - Numeric value ($)
- `items` - Line items count
- `category_name` - From filename

### 3️⃣ Database Lookup
Search `IV_MA_CATEGORY` table for:
- Category: `TRAVEL` (case-insensitive)
- Get: `APPROVAL_CRITERIA` (text field)

### 4️⃣ Approval Rules
```
IF items < 5 AND amount < $2000:
    Decision = Approved
ELSE:
    Decision = Pending
```

### 5️⃣ Database Update
Create request with:
- `CURRENT_STATUS` = 'Approved' or 'Pending'
- All extracted fields saved
- Audit trail maintained

### 6️⃣ File Organization
- **Approved** → `/Approved` folder
- **Pending** → `/Pending` folder (for review)

## Key Files

| File | Purpose |
|------|---------|
| `services/approval_evaluator.py` | Core evaluation logic |
| `app.py` (line ~145) | Integration point |
| `services/category_service.py` | Category lookup |
| `database.py` | DB status persistence |

## Usage

### Test
```bash
python test_approval_evaluator.py
```

### Example
```python
from services.approval_evaluator import ApprovalEvaluator

evaluator = ApprovalEvaluator()
result = evaluator.evaluate_with_category(
    'GBS09500_TRAVEL.pdf',
    invoice_data
)

print(result['decision'])  # 'Approved' or 'Pending'
print(result['category'])  # 'TRAVEL'
print(result['reasons'])   # ['Item count < 5', 'Amount $1800.00 < $2000']
```

## Approval Rules Explained

### ✅ Will be APPROVED
- Items: 1-4
- Amount: < $2000
- Example: $1500 for 2 items

### ⏳ Will be PENDING (needs review)
- Items: 5 or more
- Amount: $2000 or more
- Example: $2500 for 6 items

## Test Results
```
✓ Category Extraction: 4/4 passed
✓ Invoice Evaluation: 3/3 passed
✓ Full Workflow: PASSED
```

## What Happens When

| Event | Result |
|-------|--------|
| Invoice uploaded | Auto-extracted & evaluated |
| Category found | Uses approval criteria |
| Category not found | Uses default rules |
| Approved | Moved to Approved folder, DB status='Approved' |
| Pending | Moved to Pending folder, DB status='Pending' |

## Customization

### Change Approval Rules
Edit `services/approval_evaluator.py` line ~95:
```python
if item_count < 5 and total_amount < 2000:  # ← Change these
    decision = 'Approved'
```

### Add GenAI
Replace rule-based logic with GenAI call in same file.

### Add Category-Specific Rules
Use `MAXIMUMAMOUNT` field in category table:
```python
max_amount = category.MAXIMUMAMOUNT
if total_amount < max_amount:
    decision = 'Approved'
```

## Field Mapping

```
From Filename          → Field: category_name
From File Content      → Field: invoice_number
From File Content      → Field: invoice_date
From File Content      → Field: total_amount
From File Content      → Field: total_price (string)
From File Content      → Field: items (array)
From Evaluation        → Field: CURRENT_STATUS
```

## Database Tables

### Categories (IV_MA_CATEGORY)
```sql
ID                 INT
CATEGORYNAME       VARCHAR(100)
APPROVAL_CRITERIA  TEXT              ← Approval rules
MAXIMUMAMOUNT      REAL              ← Amount threshold
```

### Requests (IV_TR_REQUESTS)
```sql
ID               INT
CATEGORY_NAME    VARCHAR(100)
INVOICE_NUMBER   VARCHAR(50)
INVOICE_DATE     DATE
TOTAL_AMOUNT     DECIMAL(10,2)
CURRENT_STATUS   VARCHAR(25)        ← 'Approved' or 'Pending'
```

## Status: ✅ COMPLETE

- ✓ Category extraction
- ✓ Database lookup
- ✓ Approval evaluation
- ✓ Status persistence
- ✓ Full integration
- ✓ Test coverage

---

**For details:** See `APPROVAL_EVALUATOR_README.md` or `IMPLEMENTATION_COMPLETE.md`

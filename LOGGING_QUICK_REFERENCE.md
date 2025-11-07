# Quick Logging Reference

## Add Logging to Any New Module (3 Steps)

### Step 1: Import Logger
```python
from utils.logger_config import get_logger
logger = get_logger(__name__)
```

### Step 2: Log Entry Points
```python
def my_method(param1, param2):
    logger.info(f"[ENTER] my_method: param1={param1}, param2={param2}")
    # ... your code ...
```

### Step 3: Log Exit and Errors
```python
def my_method(param1, param2):
    logger.info(f"[ENTER] my_method: param1={param1}, param2={param2}")
    try:
        result = do_something()
        logger.info(f"[EXIT] my_method: result={result}")
        return result
    except Exception as e:
        logger.error(f"[ERROR] my_method: {type(e).__name__}: {str(e)}", exc_info=True)
        raise
```

## View Logs

### Option 1: Real-time Monitoring
```bash
cd c:\A_CODE\TRUNK\hackathon\InvoiceAI
tail -f logs/invoiceai.log
```

### Option 2: View Full Log
```bash
cat logs/invoiceai.log
```

### Option 3: Find Specific Patterns
```bash
# Find all errors
grep "\[ERROR\]" logs/invoiceai.log

# Find specific module
grep "approval_evaluator" logs/invoiceai.log

# Find specific invoice
grep "INV001" logs/invoiceai.log

# Find request processing
grep "create_request" logs/invoiceai.log
```

## Current Implementation Status

### Modules with Logging ✅
- ✅ `services/approval_evaluator.py` - Full instrumentation
- ✅ `services/category_service.py` - CRUD operations
- ✅ `services/request_service.py` - Request operations
- ✅ `database.py` - Database initialization
- ✅ `database_categories.py` - Category database
- ✅ `app.py` - Flask routes
- ✅ `utils/logger_config.py` - Central configuration

### Modules Still Need Logging (Priority Order)
- [ ] `src/invoice_processor.py` - High priority (core processing)
- [ ] `src/teams_notifier.py` - Medium priority
- [ ] `api/*.py` - API routes (create_category, create_request, etc.)

## Log Output Examples

### Successful Approval
```
2025-11-05 14:23:45 - services.approval_evaluator - INFO - [EXIT] evaluate_with_category: final_decision='Approved', category='TRAVEL'
```

### Rejected (Category Not Found)
```
2025-11-05 14:24:10 - services.approval_evaluator - INFO - [EXIT] evaluate_invoice: decision='Rejected' - category not found in database
```

### Error
```
2025-11-05 14:25:00 - services.category_service - ERROR - [ERROR] get_category_by_name: ConnectionError: database connection failed
```

## Log File Rotation

- **Max Size**: 10MB per file
- **Backup Files**: 5 backups kept
- **Location**: `logs/` directory
- **Naming**: `invoiceai.log`, `invoiceai.log.1`, `invoiceai.log.2`, etc.

When `invoiceai.log` reaches 10MB:
1. Current file renamed to `invoiceai.log.1`
2. `invoiceai.log.2` renamed to `invoiceai.log.3`
3. New `invoiceai.log` created
4. Oldest file (`invoiceai.log.5`) is deleted

## Key Metrics to Monitor

1. **API Response Time**: Compare ENTER/EXIT timestamps
2. **Database Operations**: Should complete in milliseconds
3. **GenAI API Calls**: Typically 1-2 seconds
4. **Error Rate**: Search for `[ERROR]` patterns
5. **Category Match Rate**: Count successful vs. rejected decisions

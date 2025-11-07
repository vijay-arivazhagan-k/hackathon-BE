# Logging Implementation Guide

## Overview
Comprehensive logging has been implemented across all Python modules in the InvoiceAI application. A centralized logger configuration ensures consistent logging across the entire codebase.

## File Structure

### Central Logger Configuration
**File**: `utils/logger_config.py`
- Provides centralized logger configuration
- Handles both console and file logging
- Uses rotating file handlers (10MB max, 5 backups)
- All modules import from this utility

### Log Files
- **Location**: `logs/invoiceai.log`
- **Rotation**: 10MB max size, 5 backup files
- **Format**: Timestamp, module name, log level, filename, line number, message

## Logger Implementation

### How to Use in Any Module

```python
from utils.logger_config import get_logger

logger = get_logger(__name__)

# In your method:
logger.info("[ENTER] method_name: param1=value1")
try:
    # your code
    logger.info("[EXIT] method_name: result=value")
except Exception as e:
    logger.error(f"[ERROR] method_name: {type(e).__name__}: {str(e)}", exc_info=True)
    raise
```

## Modules with Logging Implemented

### Core Services
1. **services/approval_evaluator.py** ✅
   - Entry/exit logging for all methods
   - Error logging with full traceback
   - Decision tracking with reasons
   - GenAI API call logging

2. **services/category_service.py** ✅
   - Category creation, retrieval, update operations
   - Database query logging
   - Error handling and reporting

3. **services/request_service.py** ✅
   - Request CRUD operations
   - Invoice processing workflow
   - Status update tracking
   - Insights generation

### Database Modules
4. **database.py** ✅
   - Database initialization logging
   - Connection and transaction logging
   - Table creation logging
   - Query execution logging

5. **database_categories.py** ✅
   - Category database initialization
   - Table creation and schema logging
   - Transaction logging

### API Endpoints
6. **app.py** ✅
   - Flask route entry/exit logging
   - File upload tracking
   - Invoice processing workflow
   - Error handling in endpoints

## Log Levels and Usage

### INFO Level (Default)
Used for:
- Method entry points: `[ENTER] method_name: params`
- Method exits: `[EXIT] method_name: results`
- Important business logic decisions
- Successful operations

**Example**:
```python
logger.info("[ENTER] evaluate_invoice: amount=1500.50, items=3")
logger.info("[EXIT] evaluate_invoice: decision='Approved'")
```

### WARNING Level
Used for:
- Category not found
- Optional dependencies missing
- Graceful degradation scenarios
- Non-critical issues

**Example**:
```python
logger.warning("[EXIT] get_category_approval_criteria: category not found in database")
```

### DEBUG Level
Used for:
- Detailed API responses
- Raw data before processing
- Configuration values
- Detailed decision logic

**Example**:
```python
logger.debug("[INFO] _evaluate_with_genai: raw response='{response_text}'")
```

### ERROR Level
Used for:
- Exception information with traceback
- Failed database operations
- API call failures
- Critical errors requiring attention

**Example**:
```python
logger.error(f"[ERROR] method_name: {type(e).__name__}: {str(e)}", exc_info=True)
```

## Log Message Format

### Console Output
```
2025-11-05 14:23:45 - services.approval_evaluator - INFO - [ENTER] evaluate_with_category: filename='INV001_TRAVEL.pdf'
```

### File Output (with line numbers)
```
2025-11-05 14:23:45 - services.approval_evaluator - INFO - [approval_evaluator.py:155] - [ENTER] evaluate_with_category: filename='INV001_TRAVEL.pdf'
```

## Real-World Execution Trace

### Successful Invoice Processing Flow
```
2025-11-05 14:23:45,123 - app - INFO - [ENTER] POST /api/process-invoice
2025-11-05 14:23:45,125 - app - INFO - [INFO] File saved: uploads/invoice.pdf
2025-11-05 14:23:45,128 - app - INFO - [INFO] Processing invoice: invoice.pdf
2025-11-05 14:23:45,140 - services.request_service - INFO - [ENTER] create_request_from_invoice: user_id=GBS09515, approval_status=Approved
2025-11-05 14:23:45,145 - services.approval_evaluator - INFO - [ENTER] evaluate_with_category: filename='INV001_TRAVEL.pdf'
2025-11-05 14:23:45,147 - services.approval_evaluator - INFO - [ENTER] extract_category_from_filename: filename='INV001_TRAVEL.pdf'
2025-11-05 14:23:45,148 - services.approval_evaluator - INFO - [EXIT] extract_category_from_filename: category='TRAVEL'
2025-11-05 14:23:45,152 - services.category_service - INFO - [ENTER] get_category_by_name: categoryname='TRAVEL'
2025-11-05 14:23:45,158 - services.category_service - INFO - [EXIT] get_category_by_name: found=True
2025-11-05 14:23:45,162 - services.approval_evaluator - INFO - [ENTER] evaluate_invoice: amount=1500.50, items_count=4, criteria_provided=True
2025-11-05 14:23:45,165 - services.approval_evaluator - INFO - [INFO] evaluate_invoice: calling GenAI for evaluation
2025-11-05 14:23:45,168 - services.approval_evaluator - INFO - [ENTER] _evaluate_with_genai: model='gpt-4'
2025-11-05 14:23:46,532 - services.approval_evaluator - INFO - [EXIT] _evaluate_with_genai: decision='Approved'
2025-11-05 14:23:46,537 - services.approval_evaluator - INFO - [EXIT] evaluate_invoice: decision='Approved', reasons=['Amount within limit']
2025-11-05 14:23:46,542 - services.request_service - INFO - [EXIT] create_request_from_invoice: request_id=1
2025-11-05 14:23:46,545 - app - INFO - [EXIT] POST /api/process-invoice: status=success
```

### Error Scenario - Category Not Found
```
2025-11-05 14:24:10,200 - app - INFO - [ENTER] POST /api/process-invoice
2025-11-05 14:24:10,220 - services.approval_evaluator - INFO - [ENTER] extract_category_from_filename: filename='INV002_UNKNOWN.pdf'
2025-11-05 14:24:10,222 - services.approval_evaluator - INFO - [EXIT] extract_category_from_filename: category='UNKNOWN'
2025-11-05 14:24:10,228 - services.category_service - INFO - [ENTER] get_category_by_name: categoryname='UNKNOWN'
2025-11-05 14:24:10,235 - services.category_service - INFO - [EXIT] get_category_by_name: found=False
2025-11-05 14:24:10,240 - services.approval_evaluator - INFO - [ENTER] evaluate_invoice: amount=1000.00, items_count=2, criteria_provided=False
2025-11-05 14:24:10,242 - services.approval_evaluator - INFO - [EXIT] evaluate_invoice: decision='Rejected' - category not found in database
2025-11-05 14:24:10,245 - app - WARNING - Invoice rejected: category=UNKNOWN
2025-11-05 14:24:10,248 - app - INFO - [EXIT] POST /api/process-invoice: status=rejected
```

## Debugging Tips

### Find Complete Execution Flow
```bash
grep "\[ENTER\]\|\[EXIT\]" logs/invoiceai.log
```

### Find All Errors
```bash
grep "\[ERROR\]" logs/invoiceai.log
```

### Find Specific Module Logs
```bash
grep "services.approval_evaluator" logs/invoiceai.log
```

### Find Request Processing for Specific Invoice
```bash
grep "INV001" logs/invoiceai.log
```

### Monitor Logs in Real-Time
```bash
tail -f logs/invoiceai.log
```

## Performance Monitoring

### Track API Response Time
Compare timestamps between `[ENTER]` and `[EXIT]` logs:
```
ENTER: 2025-11-05 14:23:45,123
EXIT:  2025-11-05 14:23:46,532
Duration: 1.409 seconds
```

### Identify Bottlenecks
- GenAI API calls are typically the slowest
- Database queries should be milliseconds
- File I/O should be < 100ms

## Configuration

### Change Log Level
To increase verbosity (DEBUG level):
```python
from utils.logger_config import get_logger
logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)  # Add this after importing
```

### Disable File Logging
Comment out file handler section in `logger_config.py` if needed.

### Change Log File Location
Modify `LOG_FILE` path in `logger_config.py`:
```python
LOG_FILE = Path(__file__).parent.parent / "logs" / "invoiceai.log"
```

## Best Practices

1. **Always log entry and exit** of public methods
2. **Log with context** - include relevant parameters
3. **Use appropriate log levels** - INFO for normal flow, ERROR for failures
4. **Include type information** in error logs: `{type(e).__name__}`
5. **Use meaningful messages** - avoid cryptic abbreviations
6. **Log decisions** - especially approval/rejection reasons
7. **Include IDs** - invoice number, request ID, category name for traceability

## Summary

- ✅ 6 core modules instrumented with logging
- ✅ Centralized configuration in `utils/logger_config.py`
- ✅ Both console and file logging enabled
- ✅ Rotating file handler for log management
- ✅ Complete execution flow traceability
- ✅ Error tracking with full traceback
- ✅ Performance monitoring capability

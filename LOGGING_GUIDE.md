# Approval Evaluator - Logging Guide

## Overview
Comprehensive logging has been added to `approval_evaluator.py` to track execution flow and errors.

## Log Format
```
TIMESTAMP - MODULE_NAME - LOG_LEVEL - MESSAGE
Example: 2025-11-05 14:23:45,123 - services.approval_evaluator - INFO - [ENTER] evaluate_with_category: filename='GBS09500_TRAVEL.pdf'
```

## Log Levels
- **INFO**: Normal flow (entry/exit, important decisions)
- **WARNING**: Category not found, GenAI not available (testing mode)
- **DEBUG**: Detailed API calls, raw responses
- **ERROR**: Exceptions with full traceback

## Execution Flow Logs

### 1. Entry Point: `evaluate_with_category()`
```
[ENTER] evaluate_with_category: filename='GBS09500_TRAVEL.pdf'
  ↓
[INFO] evaluate_with_category: extracted category='TRAVEL'
[INFO] evaluate_with_category: criteria_lookup_result=True
[INFO] evaluate_with_category: extracted category='TRAVEL'
  ↓
[EXIT] evaluate_with_category: final_decision='Approved', category='TRAVEL'
```

### 2. Category Extraction: `extract_category_from_filename()`
```
[ENTER] extract_category_from_filename: filename='GBS09500_TRAVEL.pdf'
[EXIT] extract_category_from_filename: category='TRAVEL'
```
**On Error:**
```
[ERROR] extract_category_from_filename: ValueError: ...details...
[EXIT] extract_category_from_filename: category='General' (default)
```

### 3. Database Lookup: `get_category_approval_criteria()`
```
[ENTER] get_category_approval_criteria: category_name='TRAVEL'
[EXIT] get_category_approval_criteria: criteria_found=True, length=250
```
**Category Not Found:**
```
[ENTER] get_category_approval_criteria: category_name='UNKNOWN'
[WARNING] [EXIT] get_category_approval_criteria: category not found in database
```
**On Database Error:**
```
[ERROR] get_category_approval_criteria: ConnectionError: database connection failed
[EXIT] get_category_approval_criteria: criteria=None (error)
```

### 4. Invoice Evaluation: `evaluate_invoice()`
```
[ENTER] evaluate_invoice: amount=1500.50, items_count=3, criteria_provided=True
[INFO] evaluate_invoice: calling GenAI for evaluation
[EXIT] evaluate_invoice: decision='Approved', reasons=['Meets all criteria']
```
**Scenario 1: Category Not Matched (Rejected)**
```
[ENTER] evaluate_invoice: amount=1500.50, items_count=3, criteria_provided=False
[EXIT] evaluate_invoice: decision='Rejected' - category not found in database
```
**Scenario 2: GenAI Not Available (Pending)**
```
[ENTER] evaluate_invoice: amount=2500.00, items_count=6, criteria_provided=True
[WARNING] [EXIT] evaluate_invoice: decision='Pending' - GenAI not available (testing mode)
```

### 5. GenAI Evaluation: `_evaluate_with_genai()`
```
[ENTER] _evaluate_with_genai: model='gpt-4'
[DEBUG] [INFO] _evaluate_with_genai: sending request to gpt-4
[DEBUG] [INFO] _evaluate_with_genai: raw response='{"decision": "Approved", "reasons": [...]}'
[EXIT] _evaluate_with_genai: decision='Approved'
```
**On GenAI Error:**
```
[ENTER] _evaluate_with_genai: model='gpt-4'
[ERROR] _evaluate_with_genai: AuthenticationError: Invalid API key
  Full traceback...
```
**On JSON Parse Error:**
```
[DEBUG] [INFO] _evaluate_with_genai: raw response='invalid json'
[ERROR] _evaluate_with_genai: JSON parsing failed: Expecting value: line 1 column 1
```

## Real-World Example

### Successful Approval Flow
```
2025-11-05 14:23:45,123 - services.approval_evaluator - INFO - [ENTER] evaluate_with_category: filename='INV001_TRAVEL.pdf'
2025-11-05 14:23:45,125 - services.approval_evaluator - INFO - [ENTER] extract_category_from_filename: filename='INV001_TRAVEL.pdf'
2025-11-05 14:23:45,126 - services.approval_evaluator - INFO - [EXIT] extract_category_from_filename: category='TRAVEL'
2025-11-05 14:23:45,128 - services.approval_evaluator - INFO - [INFO] evaluate_with_category: extracted category='TRAVEL'
2025-11-05 14:23:45,130 - services.approval_evaluator - INFO - [ENTER] get_category_approval_criteria: category_name='TRAVEL'
2025-11-05 14:23:45,135 - services.approval_evaluator - INFO - [EXIT] get_category_approval_criteria: criteria_found=True, length=310
2025-11-05 14:23:45,137 - services.approval_evaluator - INFO - [INFO] evaluate_with_category: criteria_lookup_result=True
2025-11-05 14:23:45,140 - services.approval_evaluator - INFO - [ENTER] evaluate_invoice: amount=1500.50, items_count=4, criteria_provided=True
2025-11-05 14:23:45,142 - services.approval_evaluator - INFO - [INFO] evaluate_invoice: calling GenAI for evaluation
2025-11-05 14:23:45,145 - services.approval_evaluator - INFO - [ENTER] _evaluate_with_genai: model='gpt-4'
2025-11-05 14:23:45,147 - services.approval_evaluator - DEBUG - [INFO] _evaluate_with_genai: sending request to gpt-4
2025-11-05 14:23:46,532 - services.approval_evaluator - DEBUG - [INFO] _evaluate_with_genai: raw response='{"decision": "Approved", "reasons": ["Amount within limit", "Items within limit"]}'
2025-11-05 14:23:46,535 - services.approval_evaluator - INFO - [EXIT] _evaluate_with_genai: decision='Approved'
2025-11-05 14:23:46,537 - services.approval_evaluator - INFO - [EXIT] evaluate_invoice: decision='Approved', reasons=['Amount within limit', 'Items within limit']
2025-11-05 14:23:46,540 - services.approval_evaluator - INFO - [EXIT] evaluate_with_category: final_decision='Approved', category='TRAVEL'
```

### Rejected Flow (Category Not Found)
```
2025-11-05 14:24:10,200 - services.approval_evaluator - INFO - [ENTER] evaluate_with_category: filename='INV002_UNKNOWN.pdf'
2025-11-05 14:24:10,202 - services.approval_evaluator - INFO - [ENTER] extract_category_from_filename: filename='INV002_UNKNOWN.pdf'
2025-11-05 14:24:10,203 - services.approval_evaluator - INFO - [EXIT] extract_category_from_filename: category='UNKNOWN'
2025-11-05 14:24:10,205 - services.approval_evaluator - INFO - [INFO] evaluate_with_category: extracted category='UNKNOWN'
2025-11-05 14:24:10,208 - services.approval_evaluator - INFO - [ENTER] get_category_approval_criteria: category_name='UNKNOWN'
2025-11-05 14:24:10,215 - services.approval_evaluator - WARNING - [EXIT] get_category_approval_criteria: category not found in database
2025-11-05 14:24:10,217 - services.approval_evaluator - INFO - [INFO] evaluate_with_category: criteria_lookup_result=False
2025-11-05 14:24:10,220 - services.approval_evaluator - INFO - [ENTER] evaluate_invoice: amount=1000.00, items_count=2, criteria_provided=False
2025-11-05 14:24:10,222 - services.approval_evaluator - INFO - [EXIT] evaluate_invoice: decision='Rejected' - category not found in database
2025-11-05 14:24:10,225 - services.approval_evaluator - INFO - [EXIT] evaluate_with_category: final_decision='Rejected', category='UNKNOWN'
```

### Testing Mode (GenAI Not Available)
```
2025-11-05 14:25:00,300 - services.approval_evaluator - INFO - [ENTER] evaluate_with_category: filename='INV003_TRAVEL.pdf'
...
2025-11-05 14:25:00,350 - services.approval_evaluator - INFO - [ENTER] evaluate_invoice: amount=2000.00, items_count=5, criteria_provided=True
2025-11-05 14:25:00,352 - services.approval_evaluator - INFO - [INFO] evaluate_invoice: calling GenAI for evaluation
2025-11-05 14:25:00,355 - services.approval_evaluator - WARNING - [EXIT] evaluate_invoice: decision='Pending' - GenAI not available (testing mode)
2025-11-05 14:25:00,358 - services.approval_evaluator - INFO - [EXIT] evaluate_with_category: final_decision='Pending', category='TRAVEL'
```

## Debugging Tips

1. **Full Flow Trace**: Search for `[ENTER]` and `[EXIT]` to see complete execution path
2. **Error Investigation**: Search for `[ERROR]` to find exact exception type and message
3. **API Issues**: Check `[DEBUG]` logs for raw GenAI responses
4. **Database Issues**: Look for errors in `get_category_approval_criteria`
5. **Decision Tracking**: Each decision is logged with reasons at exit point

## Configuration
Logger is configured in `approval_evaluator.py`:
- **Level**: INFO (set to DEBUG for verbose output)
- **Format**: Timestamp - Module - Level - Message
- **Output**: Console (StreamHandler)

To change log level in code:
```python
logger.setLevel(logging.DEBUG)  # For verbose output
```

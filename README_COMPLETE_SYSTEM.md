# Invoice AI - Complete System

A combined invoice processing and request management system that integrates AI-powered invoice extraction with a REST API for managing requests.

## 🏗️ System Architecture

The system consists of two main components running on a single server:

### 1. AI Processing (Flask) - `/ai/*`
- **Donut AI Model**: Extracts data from invoice images
- **Auto Approval**: Automatically approves invoices based on business rules
- **File Watcher**: Monitors incoming folder for new invoices
- **Teams Integration**: Sends notifications for pending approvals

### 2. Request Management (FastAPI) - `/api/requests/*`
- **Database**: SQLite3 in-memory database for requests
- **REST API**: Full CRUD operations for requests
- **History Tracking**: Maintains audit trail of status changes
- **Insights**: Provides statistics and analytics

## 📊 Database Schema

### IV_TR_REQUESTS Table
```sql
ID: INTEGER PRIMARY KEY AUTOINCREMENT
USER_ID: VARCHAR(25) NOT NULL
TOTAL_AMOUNT: DECIMAL(10,2)
INVOICE_DATE: DATE
INVOICE_NUMBER: VARCHAR(50)
CATEGORY_NAME: VARCHAR(100)
CURRENT_STATUS: VARCHAR(25) DEFAULT 'Pending'
COMMENTS: VARCHAR(4000)
APPROVALTYPE: VARCHAR(25) DEFAULT 'Auto'
CREATED_ON: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
UPDATED_ON: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
CREATED_BY: VARCHAR(25)
UPDATED_BY: VARCHAR(25)
```

### IV_TR_REQUEST_HISTORY Table
Same as IV_TR_REQUESTS plus:
```sql
REQUEST_ID: INTEGER NOT NULL (Foreign Key)
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Test the System
```bash
python test_system.py
```

### 3. Start the Server
```bash
python combined_app.py
```

The server will start on `http://localhost:8000`

## 📡 API Endpoints

### AI Processing Endpoints (Flask)
- `POST /ai/api/process-invoice` - Process single invoice
- `POST /ai/api/process-invoice-url` - Process invoice from URL  
- `POST /ai/api/batch-process` - Process multiple invoices
- `GET /ai/api/watcher/status` - File watcher status
- `GET /ai/api/invoice/approve/<filename>` - Approve pending invoice
- `GET /ai/api/invoice/reject/<filename>` - Reject pending invoice

### Request Management Endpoints (FastAPI)
- `GET /api/requests/` - List all requests (with pagination)
- `POST /api/requests/` - Create new request
- `GET /api/requests/{id}` - Get specific request
- `PATCH /api/requests/{id}/status` - Update request status
- `GET /api/requests/{id}/history` - Get request history
- `GET /api/requests/insights/summary` - Get statistics

### System Endpoints
- `GET /` - System overview and documentation
- `GET /health` - Combined health check
- `GET /docs` - Interactive API documentation (Swagger)

## 🔄 Processing Flow

1. **File Upload**: User places invoice in the incoming folder
2. **AI Extraction**: Donut model extracts invoice data
3. **Auto Decision**: Gen AI determines approval status based on rules
4. **File Operations**: Files moved to appropriate folders (Approved/Pending/Rejected)
5. **Database Insert**: Request automatically created in IV_TR_REQUESTS table
6. **History Tracking**: All changes recorded in IV_TR_REQUEST_HISTORY table
7. **Notifications**: Teams notifications sent for pending approvals

## 🏃‍♂️ Usage Examples

### Process an Invoice via API
```bash
curl -X POST "http://localhost:8000/ai/api/process-invoice" \
  -F "file=@invoice.jpg"
```

### List All Requests
```bash
curl "http://localhost:8000/api/requests/"
```

### Get Request Details
```bash
curl "http://localhost:8000/api/requests/1"
```

### Update Request Status
```bash
curl -X PATCH "http://localhost:8000/api/requests/1/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "Approved", "comments": "Approved by manager", "updated_by": "ADMIN"}'
```

### Get System Insights
```bash
curl "http://localhost:8000/api/requests/insights/summary"
```

## 📋 File Structure

```
InvoiceAI/
├── src/                          # Original AI processing code
│   ├── invoice_processor.py      # Donut model integration
│   └── teams_notifier.py         # Teams notifications
├── api/                          # FastAPI request management
│   └── requests.py               # Request endpoints
├── services/                     # Business logic layer
│   └── request_service.py        # Request operations
├── schemas/                      # Pydantic models
│   └── requests.py               # Request validation schemas
├── database.py                   # SQLite3 database management
├── app.py                        # Original Flask app (AI processing)
├── fastapi_app.py               # FastAPI app (request management)
├── combined_app.py              # Unified server application
├── test_system.py               # System verification tests
└── requirements.txt             # Dependencies
```

## 🔧 Configuration

### Folder Paths (in app.py)
- **INCOMING_FOLDER**: Where new invoices are dropped
- **APPROVED_FOLDER**: Auto-approved invoices
- **PENDING_FOLDER**: Invoices requiring manual approval
- **REJECTED_FOLDER**: Rejected invoices

### Auto-Approval Rules
- Invoices < $2000 with < 5 items: Auto-approved
- All others: Pending manual approval

### Teams Integration
- Webhook URL configured in `app.py`
- Notifications sent for pending approvals
- Action cards with approve/reject buttons

## 🔍 Monitoring & Debugging

### Health Checks
- `/health` - Overall system health
- `/ai/health` - AI processing component
- Database connectivity is verified on startup

### Logs
- Console logs show processing progress
- Database operations are logged
- Error handling with detailed messages

### Testing
Run `python test_system.py` to verify:
- Database operations
- Service layer functionality  
- API endpoint availability

## 🛠️ Customization

### Adding New Request Fields
1. Update database schema in `database.py`
2. Modify request models in `schemas/requests.py`
3. Update service methods in `services/request_service.py`

### Modifying Auto-Approval Rules
Edit the `_determine_approval_type()` method in `services/request_service.py`

### Adding New API Endpoints  
Add new routers in the `api/` directory and include them in `fastapi_app.py`

## 📈 Production Considerations

### Database
- Currently uses SQLite3 in-memory (data lost on restart)
- For production, consider PostgreSQL or SQL Server
- Update connection string in `database.py`

### Scaling
- Use proper WSGI server (Gunicorn) for Flask component
- Consider separating AI processing and API services
- Implement proper logging and monitoring

### Security
- Add authentication/authorization
- Validate file uploads
- Implement rate limiting
- Use HTTPS in production

## 🤝 Support

For issues or questions:
1. Check the test results: `python test_system.py`
2. Review console logs for errors
3. Verify all dependencies are installed
4. Ensure proper folder permissions for file operations
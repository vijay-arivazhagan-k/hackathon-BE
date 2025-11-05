# Microsoft Teams Integration Guide

## Overview

The InvoiceAI system automatically sends Adaptive Cards to Microsoft Teams when invoices require manual approval. This provides a seamless approval workflow directly from Teams.

## Features

### 🔔 Automatic Notifications
- Sent when invoices are marked as **PENDING**
- Triggers when either:
  - Item count >= 5, OR
  - Total amount >= $2,000

### 📋 Adaptive Card Content
Each card displays:
- Invoice number
- Invoice date
- Total price
- Item count
- Detailed list of line items (first 5 items)
- Reason for pending status

### 🔘 Interactive Actions
Three buttons on each card:
1. **📎 View Invoice** - Opens the invoice image in browser
2. **✅ Approve** - Approves and moves to Approved folder
3. **❌ Reject** - Rejects and moves to Rejected folder

## Configuration

### Webhook URL
The Teams webhook URL is configured in `app.py`:

```python
TEAMS_WEBHOOK_URL = "https://gruppobancasella.webhook.office.com/webhookb2/..."
```

### To Update Webhook:
1. Create an Incoming Webhook connector in your Teams channel
2. Copy the webhook URL
3. Update `TEAMS_WEBHOOK_URL` in `app.py`
4. Restart the API server

### API Base URL
For the action buttons to work correctly:

```python
API_BASE_URL = "http://localhost:5000"  # For local testing
# or
API_BASE_URL = "https://your-domain.com"  # For production
```

**Important**: The API must be accessible from the network where Teams users are located.

## Workflow

### 1. Invoice Processing
```
Invoice Dropped in Incoming
         ↓
   Auto-Processing
         ↓
   Approval Check
         ↓
    ┌────┴────┐
    ↓         ↓
Approved   Pending
  (Auto)   (Needs Review)
             ↓
      Teams Card Sent
```

### 2. Teams Approval
```
Teams Card Received
         ↓
  User Reviews Invoice
         ↓
    ┌────┴────┐
    ↓         ↓
Approve    Reject
    ↓         ↓
Approved   Rejected
 Folder     Folder
    ↓         ↓
Confirmation Sent
```

## Action Endpoints

### View Invoice
```
GET /api/invoice/view/{filename}
```
- Opens invoice image in browser
- Accessible from Teams card "View Invoice" button
- Serves file from Pending folder

### Approve Invoice
```
GET/POST /api/invoice/approve/{filename}
```
- Moves invoice from Pending → Approved
- Updates JSON with approval status
- Sends confirmation to Teams
- Returns HTML success page

### Reject Invoice
```
GET/POST /api/invoice/reject/{filename}
```
- Moves invoice from Pending → Rejected
- Updates JSON with rejection status
- Sends confirmation to Teams
- Returns HTML error page

## File Operations

### On Approval:
1. Read pending JSON file
2. Update `approval_status: "approved"`
3. Add `manually_approved: true`
4. Move all files to Approved folder:
   - `{filename}.jpg/png`
   - `{filename}_output.json`
   - `{filename}_output.xlsx`

### On Rejection:
1. Read pending JSON file
2. Update `approval_status: "rejected"`
3. Add `manually_rejected: true`
4. Move all files to Rejected folder:
   - `{filename}.jpg/png`
   - `{filename}_output.json`
   - `{filename}_output.xlsx`

## Folder Structure

```
Invoices/
├── Incoming/          # Drop invoices here
├── Approved/          # Auto-approved + manually approved
├── Pending/           # Awaiting manual review
└── Rejected/          # Manually rejected invoices
```

## Testing

### Test Pending Invoice Notification

1. **Create a test invoice** that triggers pending status:
   ```python
   # Either:
   - 5 or more items, OR
   - Total >= $2,000
   ```

2. **Drop in Incoming folder**

3. **Check Teams channel** for Adaptive Card

4. **Test buttons**:
   - Click "View Invoice" → Should open image
   - Click "Approve" → Should show success page
   - Click "Reject" → Should show rejection page

### Test Approval/Rejection

```powershell
# Test approve endpoint
curl http://localhost:5000/api/invoice/approve/test_invoice.jpg

# Test reject endpoint
curl http://localhost:5000/api/invoice/reject/test_invoice.jpg
```

## Troubleshooting

### Teams Card Not Appearing

**Check:**
1. Webhook URL is correct in `app.py`
2. API server is running
3. Invoice meets pending criteria
4. Check console for error messages

**Console Output:**
```
✓ Teams notification sent for invoice.jpg
```

### Action Buttons Not Working

**Verify:**
1. `API_BASE_URL` is accessible from Teams users' network
2. API server is running on specified port
3. Firewall allows incoming connections
4. Invoice file exists in Pending folder

### Invoice Not Moving

**Check:**
1. File permissions on folders
2. Invoice exists in Pending folder
3. No other process has file locked
4. Console shows move operation

## Security Considerations

### Webhook URL
- Keep webhook URL private
- Stored in code (consider environment variables for production)
- Regenerate if compromised

### API Endpoints
- Currently no authentication on approve/reject endpoints
- Consider adding authentication for production:
  ```python
  @app.route('/api/invoice/approve/<filename>')
  @require_auth  # Add authentication decorator
  def approve_invoice(filename):
      ...
  ```

### Network Security
- API must be accessible from Teams users' network
- Consider VPN or private network for production
- Use HTTPS in production (update API_BASE_URL)

## Customization

### Modify Card Appearance

Edit `src/teams_notifier.py`:

```python
def create_approval_card(self, ...):
    # Customize colors
    "style": "warning"  # or "good", "attention", "emphasis"
    
    # Customize text
    "text": "Your custom message"
    
    # Add more fields
    {
        "title": "Custom Field:",
        "value": "Custom Value"
    }
```

### Add Custom Actions

```python
"actions": [
    {
        "type": "Action.OpenUrl",
        "title": "Custom Action",
        "url": f"{self.base_url}/api/custom-endpoint/{filename}"
    }
]
```

### Modify Notifications

Edit notification timing in `app.py`:

```python
# Send for all invoices (not just pending)
if approval_status in ['approved', 'pending']:
    notifier.send_approval_request(...)

# Add custom conditions
if approval_info['total_amount'] > 5000:
    # Send to different channel or add flag
```

## Examples

### Adaptive Card JSON Structure

```json
{
  "type": "message",
  "attachments": [{
    "contentType": "application/vnd.microsoft.card.adaptive",
    "content": {
      "type": "AdaptiveCard",
      "version": "1.4",
      "body": [
        {
          "type": "Container",
          "style": "warning",
          "items": [
            {
              "type": "TextBlock",
              "text": "⏳ Invoice Pending Approval",
              "weight": "Bolder",
              "size": "Large"
            }
          ]
        }
      ],
      "actions": [
        {
          "type": "Action.OpenUrl",
          "title": "✅ Approve",
          "url": "http://localhost:5000/api/invoice/approve/invoice.jpg"
        }
      ]
    }
  }]
}
```

## Best Practices

1. **Monitor Console**: Watch for Teams notification confirmations
2. **Test Regularly**: Verify webhook and buttons work
3. **Update URLs**: Keep API_BASE_URL current
4. **Backup Webhooks**: Keep spare webhook URLs configured
5. **Log Actions**: Monitor approval/rejection logs
6. **Error Handling**: Check for failed notifications

## Support

For issues with:
- **Adaptive Cards**: Check Microsoft Teams Adaptive Cards documentation
- **Webhook Setup**: Verify Teams connector configuration
- **API Endpoints**: Check Flask server logs
- **File Operations**: Verify folder permissions

## References

- [Adaptive Cards Documentation](https://adaptivecards.io/)
- [Teams Incoming Webhooks](https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook)
- [Adaptive Cards Designer](https://adaptivecards.io/designer/)

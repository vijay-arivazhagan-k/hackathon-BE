# Network Configuration for Teams Integration

## Current Configuration

**Server IP Address**: `192.168.1.3`  
**Server Port**: `5000`  
**API Base URL**: `http://192.168.1.3:5000`

## Teams Adaptive Card Buttons

The Teams adaptive card buttons (View Invoice, Approve, Reject) use the API Base URL to create clickable links. These buttons will NOT work with `localhost` - they require a network-accessible IP address.

### Current URLs Generated:
- **View Invoice**: `http://192.168.1.3:5000/api/invoice/view/{filename}`
- **Approve**: `http://192.168.1.3:5000/api/invoice/approve/{filename}`
- **Reject**: `http://192.168.1.3:5000/api/invoice/reject/{filename}`

## How to Find Your IP Address

Run this command in PowerShell:
```powershell
ipconfig | findstr IPv4
```

Look for the IP address on your work network (typically starts with `10.` or `192.168.`)

## How to Update IP Address

If your IP address changes, update the `API_BASE_URL` in **app.py**:

```python
# Line ~41 in app.py
API_BASE_URL = "http://YOUR_NEW_IP:5000"
```

Then restart the Flask server.

## Testing Teams Buttons

1. **Ensure server is running**: `python app.py`
2. **Verify server is accessible**: Open `http://192.168.1.3:5000` in a browser
3. **Check firewall**: Windows Firewall should allow port 5000
4. **Test from Teams**: Click buttons on adaptive card

## Firewall Configuration

If buttons still don't work, you may need to allow port 5000 through Windows Firewall:

```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "Invoice AI API" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

## Troubleshooting

### Button clicks do nothing
- ✅ Server is running on `http://192.168.1.3:5000`
- ✅ IP address is correct in `app.py`
- ✅ Port 5000 is allowed through firewall
- ✅ You're on the same network as the server

### "Connection refused" error
- Server may not be running
- Check with: `curl http://192.168.1.3:5000/health`

### Different network at home
Update `API_BASE_URL` to your home network IP (e.g., `192.168.1.3:5000`)

## Production Deployment

For production, use:
- HTTPS with valid SSL certificate
- Domain name instead of IP address
- Reverse proxy (nginx, IIS)
- Authentication for approve/reject endpoints

Example production URL:
```python
API_BASE_URL = "https://invoiceai.yourcompany.com"
```

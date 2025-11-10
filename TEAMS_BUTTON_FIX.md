# Teams Adaptive Card Button Fix - Summary

## Problem
Teams adaptive card buttons (View Invoice, Approve, Reject) were not working because the API was using `localhost` URLs, which are not accessible from Teams.

## Solution Applied
Updated the API Base URL from `localhost` to your network IP address.

## Changes Made

### 1. Updated `app.py` (Line ~41)
```python
# Before:
API_BASE_URL = "http://localhost:5000"

# After:
API_BASE_URL = "http://192.168.1.3:5000"
```

### 2. Updated `TEAMS_INTEGRATION.md`
Added clarification that `localhost` will NOT work for Teams buttons - must use network IP.

### 3. Created Helper Files

#### `NETWORK_CONFIG.md`
- Quick reference for network configuration
- How to find and update IP address
- Troubleshooting guide

#### `setup_firewall.ps1`
- PowerShell script to configure Windows Firewall
- Allows port 5000 through firewall
- Run as Administrator if buttons still don't work

#### `test_teams_network.py`
- Test script to verify network accessibility
- Checks if API is reachable from network IP
- Identifies common issues

## How to Use

### Step 1: Restart the Server
If your server is currently running, restart it to pick up the new IP address:

1. Stop the current server (Ctrl+C in the terminal)
2. Restart: `python app.py`

### Step 2: Configure Firewall (If Needed)
If buttons still don't work after restart:

1. Open PowerShell as **Administrator**
2. Navigate to project: `cd C:\A_CODE\TRUNK\hackathon\InvoiceAI`
3. Run: `.\setup_firewall.ps1`

### Step 3: Test the Connection
```bash
python test_teams_network.py
```

This will verify that:
- Server is running on localhost ✓
- Server is accessible from network IP ✓
- Teams buttons will work ✓

## Teams Adaptive Card URLs

The buttons will now use these URLs:

- **View Invoice**: `http://192.168.1.3:5000/api/invoice/view/{filename}`
- **Approve**: `http://192.168.1.3:5000/api/invoice/approve/{filename}`
- **Reject**: `http://192.168.1.3:5000/api/invoice/reject/{filename}`

## Testing Teams Buttons

1. Drop an invoice in the Incoming folder that triggers "Pending" status:
   - Total amount > 3000, OR
   - 5 or more items

2. Check Teams for the adaptive card

3. Click the buttons:
   - **View Invoice** → Opens image in browser
   - **Approve** → Moves to Approved folder, shows success page
   - **Reject** → Moves to Rejected folder, shows rejection page

## If IP Address Changes

Your IP might change if you:
- Connect to a different network
- Restart your computer
- Work from home

To update:

1. Find new IP: `ipconfig | findstr IPv4`
2. Update in `app.py`: `API_BASE_URL = "http://NEW_IP:5000"`
3. Restart server

## Verification Checklist

Before testing Teams buttons:

- [ ] Server is running (`python app.py`)
- [ ] Server shows: "Server is ready!"
- [ ] API_BASE_URL is set to network IP (not localhost)
- [ ] Port 5000 is allowed through firewall
- [ ] Can access `http://192.168.1.3:5000/health` in browser
- [ ] Teams webhook is configured correctly

## Common Issues

### Issue 1: "This site can't be reached"
**Cause**: Firewall blocking port 5000  
**Solution**: Run `setup_firewall.ps1` as Administrator

### Issue 2: "Connection refused"
**Cause**: Server not running  
**Solution**: Start server with `python app.py`

### Issue 3: Buttons work at office but not at home
**Cause**: Different network IP at home  
**Solution**: Update API_BASE_URL to home network IP

### Issue 4: View button works but Approve/Reject don't
**Cause**: Files might be locked or missing  
**Solution**: Check Pending folder has the invoice files

## Server Configuration

The Flask server is configured to accept connections from any network interface:

```python
app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
```

This is correct and allows Teams to access the API.

## Security Notes

**Current Setup**: No authentication on approve/reject endpoints  
**Recommended for Production**:
- Add authentication middleware
- Use HTTPS with SSL certificate
- Implement user authorization
- Use reverse proxy (IIS, nginx)

## Next Steps

1. **Restart your server** to apply the IP address change
2. **Test with Teams** by processing a pending invoice
3. **Configure firewall** if buttons don't work
4. **Monitor logs** for any connection errors

## Support

If buttons still don't work after following these steps:

1. Run `python test_teams_network.py` - share the output
2. Check Windows Firewall logs
3. Verify network connectivity: `ping 192.168.1.3`
4. Test manually: Open `http://192.168.1.3:5000/api/watcher/status` in browser

---

**Status**: ✅ Configuration updated  
**Next**: Restart server to apply changes

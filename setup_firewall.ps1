# Windows Firewall Configuration for Invoice AI API
# Run this script as Administrator to allow port 5000 through Windows Firewall

Write-Host "Configuring Windows Firewall for Invoice AI API..." -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator', then run this script again." -ForegroundColor Yellow
    pause
    exit 1
}

# Remove existing rule if it exists
$existingRule = Get-NetFirewallRule -DisplayName "Invoice AI API" -ErrorAction SilentlyContinue
if ($existingRule) {
    Write-Host "Removing existing firewall rule..." -ForegroundColor Yellow
    Remove-NetFirewallRule -DisplayName "Invoice AI API"
}

# Create new firewall rule
Write-Host "Creating firewall rule to allow port 5000..." -ForegroundColor Green
New-NetFirewallRule -DisplayName "Invoice AI API" `
    -Direction Inbound `
    -LocalPort 5000 `
    -Protocol TCP `
    -Action Allow `
    -Profile Any `
    -Description "Allows incoming connections to Invoice AI Flask API on port 5000"

Write-Host ""
Write-Host "✅ Firewall rule created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Invoice AI API is now accessible on:" -ForegroundColor Cyan
Write-Host "  - http://192.168.1.3:5000" -ForegroundColor White
Write-Host "  - http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "You can now use Teams adaptive card buttons." -ForegroundColor Green
Write-Host ""

# Test if server is running
Write-Host "Testing if server is running..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Server is running!" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "⚠️  Server is NOT running yet." -ForegroundColor Yellow
    Write-Host "Start the server with: python app.py" -ForegroundColor White
}

Write-Host ""
pause

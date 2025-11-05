# InvoiceAI - GitHub Quick Setup Script
# Run this script to initialize and push to GitHub

Write-Host "================================" -ForegroundColor Cyan
Write-Host "InvoiceAI - GitHub Setup Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is installed
try {
    $gitVersion = git --version
    Write-Host "✓ Git installed: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Git is not installed. Please install from https://git-scm.com/" -ForegroundColor Red
    exit 1
}

# Check if already a git repository
if (Test-Path .git) {
    Write-Host "✓ Git repository already initialized" -ForegroundColor Green
} else {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
    Write-Host "✓ Git repository initialized" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Git Configuration" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Get user name and email
$userName = git config --global user.name
$userEmail = git config --global user.email

if ([string]::IsNullOrEmpty($userName)) {
    Write-Host ""
    $userName = Read-Host "Enter your name"
    git config --global user.name "$userName"
}

if ([string]::IsNullOrEmpty($userEmail)) {
    Write-Host ""
    $userEmail = Read-Host "Enter your email"
    git config --global user.email "$userEmail"
}

Write-Host ""
Write-Host "Git User: $userName <$userEmail>" -ForegroundColor Green

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Repository Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Get GitHub username and repository name
Write-Host ""
$githubUsername = Read-Host "Enter your GitHub username"
$repoName = Read-Host "Enter repository name (default: InvoiceAI)"

if ([string]::IsNullOrEmpty($repoName)) {
    $repoName = "InvoiceAI"
}

$repoUrl = "https://github.com/$githubUsername/$repoName.git"

Write-Host ""
Write-Host "Repository URL: $repoUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: Create this repository on GitHub first!" -ForegroundColor Yellow
Write-Host "1. Go to https://github.com/new" -ForegroundColor Yellow
Write-Host "2. Repository name: $repoName" -ForegroundColor Yellow
Write-Host "3. Description: AI-powered invoice processing with Teams integration" -ForegroundColor Yellow
Write-Host "4. Choose Public or Private" -ForegroundColor Yellow
Write-Host "5. DO NOT initialize with README, .gitignore, or license" -ForegroundColor Yellow
Write-Host "6. Click 'Create repository'" -ForegroundColor Yellow
Write-Host ""

$confirm = Read-Host "Have you created the repository on GitHub? (yes/no)"

if ($confirm -ne "yes" -and $confirm -ne "y") {
    Write-Host ""
    Write-Host "Please create the repository on GitHub first, then run this script again." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Adding Files" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

Write-Host "Adding all files to git..." -ForegroundColor Yellow
git add .

Write-Host ""
Write-Host "Files to be committed:" -ForegroundColor Cyan
git status --short

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Creating Commit" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

$commitMessage = @"
Initial commit: InvoiceAI - Intelligent Invoice Processing System

Features:
- Donut transformer model for invoice data extraction
- Automatic approval system with configurable rules
- Microsoft Teams integration with Adaptive Cards
- REST API for invoice processing
- Automatic file watcher for incoming invoices
- Excel and JSON output generation
- Four-stage approval workflow (Incoming → Approved/Pending/Rejected)

Tech Stack:
- Python 3.11+
- PyTorch & Transformers (Donut model)
- Flask REST API
- Watchdog for file monitoring
- Microsoft Teams webhooks
- Pandas & OpenPyXL for Excel generation
"@

Write-Host "Creating commit..." -ForegroundColor Yellow
git commit -m "$commitMessage"

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Connecting to GitHub" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Check if remote already exists
$existingRemote = git remote get-url origin 2>$null

if ($existingRemote) {
    Write-Host "Remote 'origin' already exists: $existingRemote" -ForegroundColor Yellow
    $updateRemote = Read-Host "Update remote URL? (yes/no)"
    
    if ($updateRemote -eq "yes" -or $updateRemote -eq "y") {
        git remote set-url origin $repoUrl
        Write-Host "✓ Remote URL updated" -ForegroundColor Green
    }
} else {
    Write-Host "Adding remote repository..." -ForegroundColor Yellow
    git remote add origin $repoUrl
    Write-Host "✓ Remote added: $repoUrl" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Pushing to GitHub" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Setting main branch..." -ForegroundColor Yellow
git branch -M main

Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "You may be prompted for your GitHub credentials." -ForegroundColor Cyan
Write-Host "Use your GitHub Personal Access Token as password" -ForegroundColor Cyan
Write-Host "Create token at: https://github.com/settings/tokens" -ForegroundColor Cyan
Write-Host ""

try {
    git push -u origin main
    
    Write-Host ""
    Write-Host "================================" -ForegroundColor Green
    Write-Host "✓ SUCCESS!" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Repository pushed to GitHub successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "View your repository at:" -ForegroundColor Cyan
    Write-Host "https://github.com/$githubUsername/$repoName" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Add repository description and topics on GitHub" -ForegroundColor Yellow
    Write-Host "2. Review README.md on GitHub" -ForegroundColor Yellow
    Write-Host "3. Star your repository ⭐" -ForegroundColor Yellow
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "✗ Error pushing to GitHub" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Make sure the repository exists on GitHub" -ForegroundColor Yellow
    Write-Host "2. Check your internet connection" -ForegroundColor Yellow
    Write-Host "3. Verify your GitHub credentials" -ForegroundColor Yellow
    Write-Host "4. Use Personal Access Token instead of password" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "For help, see: GITHUB_COMMIT_GUIDE.md" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

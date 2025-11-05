# GitHub Commit Guide for InvoiceAI

## Prerequisites

1. **Git installed** - Check with: `git --version`
2. **GitHub account** - Create at https://github.com if you don't have one
3. **GitHub CLI (optional)** - Or use web interface to create repository

## Step-by-Step Instructions

### Option 1: Using Command Line (Recommended)

#### Step 1: Initialize Git Repository

Open PowerShell in the project directory and run:

```powershell
cd C:\InvoiceAI

# Initialize git repository
git init

# Check git status
git status
```

#### Step 2: Configure Git (First Time Only)

```powershell
# Set your name and email
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Verify configuration
git config --list
```

#### Step 3: Create Repository on GitHub

**Option A: Using GitHub Web Interface**
1. Go to https://github.com/new
2. Repository name: `InvoiceAI` (or your preferred name)
3. Description: "AI-powered invoice processing system with Teams integration"
4. Choose Public or Private
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

**Option B: Using GitHub CLI** (if installed)
```powershell
gh repo create InvoiceAI --public --source=. --remote=origin
```

#### Step 4: Add Files to Git

```powershell
# Add all files
git add .

# Check what will be committed
git status

# If you see files you don't want to commit, update .gitignore and run:
git rm --cached <filename>
git add .gitignore
```

#### Step 5: Create Initial Commit

```powershell
git commit -m "Initial commit: InvoiceAI with Donut model, approval system, and Teams integration"
```

#### Step 6: Connect to GitHub Repository

Replace `YOUR_USERNAME` with your actual GitHub username:

```powershell
# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/InvoiceAI.git

# Verify remote
git remote -v
```

#### Step 7: Push to GitHub

```powershell
# Push to main branch
git branch -M main
git push -u origin main
```

**If prompted for credentials:**
- Use Personal Access Token (PAT) instead of password
- Create PAT at: https://github.com/settings/tokens
- Use token as password when prompted

---

### Option 2: Using GitHub Desktop

1. **Download GitHub Desktop** from https://desktop.github.com/
2. **Install and sign in** with your GitHub account
3. **Add repository**:
   - File → Add Local Repository
   - Choose `C:\InvoiceAI`
   - If not a git repo, click "create a repository"
4. **Commit changes**:
   - Write commit message: "Initial commit"
   - Click "Commit to main"
5. **Publish repository**:
   - Click "Publish repository"
   - Choose name and visibility
   - Click "Publish Repository"

---

## Commit Message Template

For the initial commit, use:

```
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
```

---

## Verify Upload

After pushing, verify at: `https://github.com/YOUR_USERNAME/InvoiceAI`

You should see:
- ✅ All project files
- ✅ README.md displayed on main page
- ✅ Folder structure intact
- ✅ .gitignore working (no uploads/, output/ contents)

---

## Add Repository Description

On GitHub repository page:
1. Click ⚙️ next to "About"
2. Add description: "AI-powered invoice processing with approval workflow and Teams integration"
3. Add topics (tags):
   - `invoice-processing`
   - `ocr`
   - `donut-model`
   - `teams-integration`
   - `python`
   - `machine-learning`
   - `document-ai`
   - `adaptive-cards`

---

## Create README Badge (Optional)

Add to top of README.md:

```markdown
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
```

---

## Future Updates

To commit future changes:

```powershell
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add feature: description of changes"

# Push to GitHub
git push origin main
```

---

## Common Issues & Solutions

### Issue: "fatal: not a git repository"
**Solution:** Run `git init` first

### Issue: "Authentication failed"
**Solution:** Use Personal Access Token instead of password
1. Go to https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scopes: `repo` (full control)
4. Use token as password

### Issue: "remote origin already exists"
**Solution:** 
```powershell
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/InvoiceAI.git
```

### Issue: Large files warning
**Solution:** Check .gitignore is working properly
```powershell
git rm --cached <large-file>
git commit --amend
```

### Issue: Push rejected
**Solution:** Pull first, then push
```powershell
git pull origin main --rebase
git push origin main
```

---

## Security Notes

⚠️ **Before Committing:**

1. **Remove sensitive data** from code:
   - Webhook URLs (move to environment variables)
   - API keys
   - Database credentials
   - File paths with usernames

2. **Update app.py** to use environment variables:
   ```python
   import os
   TEAMS_WEBHOOK_URL = os.getenv('TEAMS_WEBHOOK_URL', 'your-default-url')
   ```

3. **Create .env.example** file:
   ```
   TEAMS_WEBHOOK_URL=https://your-webhook-url
   API_BASE_URL=http://localhost:5000
   ```

4. **Add to .gitignore**:
   ```
   .env
   config.local.json
   ```

---

## Repository Settings (Recommended)

After pushing:

1. **Add topics/tags** for discoverability
2. **Enable Issues** for bug tracking
3. **Add LICENSE** file (MIT recommended)
4. **Enable Discussions** for community questions
5. **Set up branch protection** (for collaborative projects)

---

## Quick Reference Commands

```powershell
# Check status
git status

# View commit history
git log --oneline

# View remote URL
git remote -v

# Update from GitHub
git pull origin main

# Create new branch
git checkout -b feature-name

# Switch branches
git checkout main

# View changes
git diff

# Undo last commit (keep changes)
git reset --soft HEAD~1

# View file history
git log --follow <filename>
```

---

## Next Steps After Upload

1. ✅ Verify all files uploaded correctly
2. 📝 Add detailed documentation if needed
3. 🏷️ Create first release/tag (v1.0.0)
4. 📋 Add GitHub Actions for CI/CD (optional)
5. 🌟 Star your own repository
6. 📢 Share with team/community

---

## Need Help?

- GitHub Docs: https://docs.github.com/
- Git Documentation: https://git-scm.com/doc
- GitHub Desktop: https://docs.github.com/desktop

# Quick Start: Commit InvoiceAI to GitHub

## 🚀 Fastest Method (PowerShell Script)

### Step 1: Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `InvoiceAI`
3. **DO NOT** check any initialization options
4. Click "Create repository"

### Step 2: Run Setup Script
```powershell
cd C:\InvoiceAI
.\setup_github.ps1
```

The script will:
- ✅ Initialize git repository
- ✅ Configure git settings
- ✅ Add all files
- ✅ Create commit
- ✅ Push to GitHub

---

## 📋 Manual Method (Command Line)

If you prefer manual control:

```powershell
# 1. Initialize git
cd C:\InvoiceAI
git init

# 2. Configure git (first time only)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 3. Add files
git add .

# 4. Commit
git commit -m "Initial commit: InvoiceAI with Donut model and Teams integration"

# 5. Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/InvoiceAI.git

# 6. Push
git branch -M main
git push -u origin main
```

---

## 🔑 Authentication

When prompted for password, use **Personal Access Token**:

1. Create at: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scope: `repo` (Full control of private repositories)
4. Copy the token
5. Use it as your password when git prompts

---

## ✅ Verify Success

After pushing, check:
- https://github.com/YOUR_USERNAME/InvoiceAI

You should see all project files!

---

## 📦 What Gets Committed

**Included:**
- ✅ All source code (`*.py`)
- ✅ Configuration files (`config.json`, `requirements.txt`)
- ✅ Documentation (`*.md`)
- ✅ Empty folder placeholders (`.gitkeep`)

**Excluded (via .gitignore):**
- ❌ Python cache (`__pycache__`)
- ❌ Virtual environments (`venv/`)
- ❌ Uploaded files (`uploads/*`)
- ❌ Generated outputs (`output/*.json`)
- ❌ Invoice images (`invoices/*.jpg`)
- ❌ IDE settings (`.vscode/`)
- ❌ Model cache files

---

## 🎯 Repository Info to Add

After uploading, add on GitHub:

**Description:**
```
AI-powered invoice processing system with automatic approval workflow and Microsoft Teams integration using Donut transformer model
```

**Topics:**
```
invoice-processing
ocr
donut-model
teams-integration
python
machine-learning
document-ai
adaptive-cards
automation
rest-api
```

---

## 📝 For Detailed Instructions

See: `GITHUB_COMMIT_GUIDE.md`

---

## ⚠️ Before Committing (Security)

Consider removing sensitive data:

1. **Webhook URL** in `app.py`:
   ```python
   # Instead of hardcoded URL, use environment variable
   TEAMS_WEBHOOK_URL = os.getenv('TEAMS_WEBHOOK_URL', '')
   ```

2. **File paths** with usernames:
   ```python
   # Use relative paths or env variables
   INCOMING_FOLDER = os.getenv('INCOMING_FOLDER', './invoices/incoming')
   ```

3. Create `.env.example`:
   ```
   TEAMS_WEBHOOK_URL=your-webhook-url-here
   INCOMING_FOLDER=C:\path\to\incoming
   APPROVED_FOLDER=C:\path\to\approved
   PENDING_FOLDER=C:\path\to\pending
   REJECTED_FOLDER=C:\path\to\rejected
   ```

---

## 🆘 Common Issues

### "Authentication failed"
→ Use Personal Access Token, not password

### "Permission denied"
→ Check repository exists and you have write access

### "Remote already exists"
→ Run: `git remote remove origin` then add again

### "Nothing to commit"
→ Check `.gitignore` isn't excluding everything

---

## 📞 Need Help?

- Full guide: `GITHUB_COMMIT_GUIDE.md`
- GitHub Docs: https://docs.github.com/
- Git Help: `git help`

---

**Ready? Run the script or follow manual steps above!** 🚀

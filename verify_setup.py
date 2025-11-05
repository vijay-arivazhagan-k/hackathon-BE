"""
Test script to verify the invoice processing system is set up correctly
"""

import sys
import os

print("="*60)
print("Invoice AI - System Verification")
print("="*60)
print()

# Test 1: Check Python version
print("1. Checking Python version...")
version = sys.version_info
if version.major == 3 and version.minor >= 11:
    print(f"   ✓ Python {version.major}.{version.minor}.{version.micro} (Compatible)")
else:
    print(f"   ✗ Python {version.major}.{version.minor}.{version.micro} (Requires 3.11+)")
print()

# Test 2: Check required packages
print("2. Checking required packages...")
required_packages = [
    'torch',
    'transformers',
    'PIL',
    'flask',
    'flask_cors',
    'watchdog',
    'openpyxl',
    'pandas'
]

all_installed = True
for package in required_packages:
    try:
        if package == 'PIL':
            __import__('PIL')
        else:
            __import__(package)
        print(f"   ✓ {package}")
    except ImportError:
        print(f"   ✗ {package} - NOT INSTALLED")
        all_installed = False
print()

# Test 3: Check directories
print("3. Checking directories...")
directories = [
    ('Incoming', r"C:\Users\gbs09515\OneDrive - Sella\Documents\Invoices\Incoming"),
    ('Outgoing', r"C:\Users\gbs09515\OneDrive - Sella\Documents\Invoices\Outgoing"),
    ('Uploads', 'uploads'),
    ('Output', 'output')
]

for name, path in directories:
    if os.path.exists(path):
        print(f"   ✓ {name}: {path}")
    else:
        print(f"   ✗ {name}: {path} - NOT FOUND")
print()

# Test 4: Check configuration
print("4. Checking configuration...")
if os.path.exists('config.json'):
    print("   ✓ config.json exists")
else:
    print("   ✗ config.json - NOT FOUND")
print()

# Test 5: Check source files
print("5. Checking source files...")
source_files = [
    'src/invoice_processor.py',
    'app.py',
    'main.py'
]

for file in source_files:
    if os.path.exists(file):
        print(f"   ✓ {file}")
    else:
        print(f"   ✗ {file} - NOT FOUND")
print()

# Summary
print("="*60)
if all_installed:
    print("✓ All checks passed! System is ready.")
    print("\nTo start the API server:")
    print("  python app.py")
    print("\nTo process invoices via CLI:")
    print("  python main.py")
else:
    print("✗ Some packages are missing. Install them with:")
    print("  pip install -r requirements.txt")
print("="*60)

# Python Virtual Environment Setup Instructions

## Step 1: Install Python

If Python is not installed on your system:

1. Download Python 3.8 or later from: https://www.python.org/downloads/
2. **IMPORTANT**: During installation, check the box that says **"Add Python to PATH"**
3. Complete the installation

## Step 2: Verify Python Installation

Open a terminal (PowerShell or Command Prompt) and run:

```bash
python --version
```

You should see something like: `Python 3.x.x`

If that doesn't work, try:
```bash
py --version
```

## Step 3: Create Virtual Environment

### Option A: Using Batch Script (Command Prompt)
```bash
setup_venv.bat
```

### Option B: Using PowerShell Script
```powershell
.\setup_venv.ps1
```

### Option C: Manual Setup
```bash
python -m venv venv
```

## Step 4: Activate Virtual Environment

### Option A: Using Batch Script (Command Prompt)
```bash
activate_venv.bat
```

### Option B: Using PowerShell Script
```powershell
.\activate_venv.ps1
```

**Note**: If you get an execution policy error in PowerShell, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Option C: Manual Activation

**Command Prompt:**
```bash
venv\Scripts\activate
```

**PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Git Bash / Linux / Mac:**
```bash
source venv/bin/activate
```

## Step 5: Verify Virtual Environment

Once activated, you should see `(venv)` at the beginning of your command prompt:

```
(venv) C:\Users\bobby\SysArch_V1>
```

## Step 6: Use the Library

With the virtual environment activated, you can now:

1. Initialize the database:
   ```bash
   python manage_assembly.py init-db
   ```

2. Use the CLI commands (see README.md for details)

3. Import the library in Python:
   ```python
   from sysarch import DatabaseManager, Part, Assembly
   ```

## Deactivating the Virtual Environment

When you're done, deactivate the virtual environment:

```bash
deactivate
```

## Troubleshooting

### "Python was not found"
- Make sure Python is installed
- Make sure Python was added to PATH during installation
- Try restarting your terminal after installing Python
- Try using `py` instead of `python` on Windows

### "venv module not found"
- Make sure you're using Python 3.8 or later
- Try reinstalling Python with "Add Python to PATH" checked

### PowerShell Execution Policy Error
Run this command in PowerShell (as Administrator if needed):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Virtual Environment Already Exists
If you see an error that the virtual environment already exists, you can:
- Delete the `venv` folder and run setup again
- Or just activate the existing one with `activate_venv.bat` or `activate_venv.ps1`



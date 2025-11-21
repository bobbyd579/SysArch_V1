# PowerShell script for creating a Python virtual environment on Windows

Write-Host "Checking for Python installation..." -ForegroundColor Cyan

# Try different Python commands
$pythonCmd = $null

if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
}

if ($null -eq $pythonCmd) {
    Write-Host ""
    Write-Host "ERROR: Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.8 or later from:" -ForegroundColor Yellow
    Write-Host "  https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Python found: $pythonCmd" -ForegroundColor Green
& $pythonCmd --version
Write-Host ""

Write-Host "Creating virtual environment in 'venv' folder..." -ForegroundColor Cyan
& $pythonCmd -m venv venv

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Failed to create virtual environment." -ForegroundColor Red
    Write-Host "Make sure you have the 'venv' module installed." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Virtual environment created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "To activate the virtual environment, run:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "Or use the activate_venv.ps1 script." -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to continue"



# PowerShell script to activate the Python virtual environment

if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup_venv.ps1 first to create the virtual environment." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& "venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host "You can now use Python and install packages." -ForegroundColor Cyan
Write-Host ""
Write-Host "To deactivate, type: deactivate" -ForegroundColor Yellow
Write-Host ""



# PowerShell script to push to GitHub
# Replace YOUR_USERNAME with your actual GitHub username

$username = Read-Host "Enter your GitHub username"

if ([string]::IsNullOrWhiteSpace($username)) {
    Write-Host "Username is required!" -ForegroundColor Red
    exit 1
}

Write-Host "Setting up remote and pushing to GitHub..." -ForegroundColor Cyan

# Add remote
git remote add origin "https://github.com/$username/SysArch_V1.git"

# Check if remote was added successfully
if ($LASTEXITCODE -ne 0) {
    Write-Host "Remote might already exist. Removing and re-adding..." -ForegroundColor Yellow
    git remote remove origin
    git remote add origin "https://github.com/$username/SysArch_V1.git"
}

# Rename branch to main (GitHub default)
git branch -M main

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Success! Your code has been pushed to GitHub!" -ForegroundColor Green
    Write-Host "Repository URL: https://github.com/$username/SysArch_V1" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "Push failed. You may need to authenticate." -ForegroundColor Red
    Write-Host "If using HTTPS, you'll need a Personal Access Token instead of a password." -ForegroundColor Yellow
    Write-Host "Create one at: https://github.com/settings/tokens" -ForegroundColor Yellow
}


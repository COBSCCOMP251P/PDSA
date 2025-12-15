# Snake and Ladder Game - Frontend Server
# PowerShell script to serve the frontend

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Snake and Ladder Game - Frontend" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}
Write-Host "Found: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Navigate to frontend directory
Set-Location "frontend"

Write-Host "Starting frontend server..." -ForegroundColor Green
Write-Host ""
Write-Host "Frontend will be available at:" -ForegroundColor Cyan
Write-Host "  • http://localhost:8080" -ForegroundColor White
Write-Host ""
Write-Host "Make sure backend is running at http://localhost:8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start Python HTTP server
python -m http.server 8080

# Return to parent directory
Set-Location ".."

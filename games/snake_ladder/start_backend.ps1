# Snake and Ladder Game - Startup Script
# PowerShell script to start the backend server

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Snake and Ladder Game - Backend" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org/" -ForegroundColor Red
    exit 1
}
Write-Host "Found: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
$venvPath = "..\..\venv"
if (Test-Path $venvPath) {
    Write-Host "Virtual environment found, activating..." -ForegroundColor Yellow
    & "$venvPath\Scripts\Activate.ps1"
} else {
    Write-Host "No virtual environment found (optional)" -ForegroundColor Yellow
}
Write-Host ""

# Check if dependencies are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$fastapi = pip show fastapi 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Dependencies not installed" -ForegroundColor Yellow
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r ..\..\requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}
Write-Host "Dependencies OK" -ForegroundColor Green
Write-Host ""

# Check if .env file exists
$envPath = "..\..\\.env"
if (-not (Test-Path $envPath)) {
    Write-Host "WARNING: .env file not found" -ForegroundColor Yellow
    Write-Host "Please create .env file from .env.example" -ForegroundColor Yellow
    Write-Host "Copy .env.example to .env and update database credentials" -ForegroundColor Yellow
    Write-Host ""
}

# Navigate to backend directory
Set-Location "..\..\shared\backend"

# Start the server
Write-Host "Starting FastAPI backend server..." -ForegroundColor Green
Write-Host ""
Write-Host "Server will be available at:" -ForegroundColor Cyan
Write-Host "  • API: http://localhost:8000" -ForegroundColor White
Write-Host "  • Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  • Health: http://localhost:8000/api/health" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run the server
python main.py

# Return to original directory
Set-Location "..\..\games\snake_ladder"

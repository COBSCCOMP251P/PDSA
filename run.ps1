# ========================================
# PDSA Eight Queens - Simple Start Script
# ========================================
# Run this in PowerShell to start the game

Write-Host ""
Write-Host "========================================"
Write-Host "  PDSA Eight Queens Game - Starting..."
Write-Host "========================================"
Write-Host ""

# Go to project folder
Set-Location $PSScriptRoot

# Activate virtual environment
& ".\.venv\Scripts\Activate.ps1"

Write-Host "Server starting at: http://127.0.0.1:8000/games/eight_queens/frontend/index.html" -ForegroundColor Green
Write-Host "API Docs at: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server"
Write-Host ""

# Start server
python -m uvicorn shared.backend.main:app --reload --host 127.0.0.1 --port 8000

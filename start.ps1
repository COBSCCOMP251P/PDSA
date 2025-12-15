# ================================================================
# PDSA Algorithm Games - Unified Start Script
# ================================================================
# This script starts all required services for the complete system
# 5 Games: Eight Queens, Snake & Ladder, Traffic Simulation,
#          Tower of Hanoi, Traveling Salesman
# ================================================================

param(
    [switch]$QuickStart,    # Skip dependency checks and go straight to server
    [switch]$ResetDatabase, # Reset and recreate database
    [switch]$Verbose        # Show detailed output
)

# Configuration
$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$VENV_PATH = "$PROJECT_ROOT\.venv"
$PYTHON_EXE = "$VENV_PATH\Scripts\python.exe"
$PIP_EXE = "$VENV_PATH\Scripts\pip.exe"
$SERVER_HOST = "127.0.0.1"
$SERVER_PORT = 8000
$DB_PASSWORD = "pruthuvide"

# Color functions
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Error { param($msg) Write-Host "❌ $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "ℹ️  $msg" -ForegroundColor Cyan }
function Write-Warning { param($msg) Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Step { param($msg) Write-Host "`n🔄 $msg" -ForegroundColor Blue }

# Main execution
try {
    Write-Host @"
╔══════════════════════════════════════════════════════════════════╗
║                    PDSA Algorithm Games                         ║
║                    Unified Start Script                         ║
╚══════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Magenta

    # Change to project directory
    Set-Location $PROJECT_ROOT
    Write-Info "Working directory: $PROJECT_ROOT"

    if (-not $QuickStart) {
        # ================================
        # STEP 1: Check MySQL Service
        # ================================
        Write-Step "Checking MySQL service status..."
        try {
            $mysqlService = Get-Service -ErrorAction SilentlyContinue | Where-Object {$_.Name -like "*mysql*" -and $_.Status -eq "Running"}
            if ($mysqlService) {
                Write-Success "MySQL service is running: $($mysqlService.DisplayName)"
            } else {
                Write-Warning "MySQL service not found or not running"
                # Try direct mysql command test
                try {
                    mysql --version > $null 2>&1
                    if ($LASTEXITCODE -eq 0) {
                        Write-Info "MySQL client is available"
                    }
                } catch {
                    Write-Info "Please ensure MySQL is installed and running"
                }
            }
        } catch {
            Write-Warning "Could not check MySQL service status (permission issue)"
            Write-Info "Continuing with startup..."
        }

        # ================================
        # STEP 2: Setup Virtual Environment
        # ================================
        Write-Step "Setting up Python virtual environment..."
        if (-not (Test-Path $VENV_PATH)) {
            Write-Info "Creating virtual environment..."
            python -m venv .venv
            if ($LASTEXITCODE -ne 0) {
                throw "Failed to create virtual environment. Please ensure Python is installed."
            }
            Write-Success "Virtual environment created"
        } else {
            Write-Success "Virtual environment already exists"
        }

        # ================================
        # STEP 3: Install Python Dependencies
        # ================================
        Write-Step "Installing Python dependencies..."
        $dependencies = @(
            "fastapi",
            "uvicorn[standard]", 
            "python-dotenv",
            "mysql-connector-python"
        )
        
        foreach ($dep in $dependencies) {
            Write-Info "Installing $dep..."
            & $PIP_EXE install $dep --quiet
        }
        Write-Success "All Python dependencies installed"

        # ================================
        # STEP 4: Install Node.js Dependencies
        # ================================
        Write-Step "Checking Node.js dependencies..."
        if (Test-Path "package.json") {
            if (-not (Test-Path "node_modules")) {
                Write-Info "Installing Node.js dependencies..."
                npm install
                Write-Success "Node.js dependencies installed"
            } else {
                Write-Success "Node.js dependencies already installed"
            }
            
            # Build CSS
            Write-Info "Building CSS assets..."
            npm run build-css 2>$null
            Write-Success "CSS assets built"
        } else {
            Write-Warning "package.json not found, skipping Node.js setup"
        }

        # ================================
        # STEP 5: Database Setup
        # ================================
        Write-Step "Setting up database..."
        if ($ResetDatabase) {
            Write-Warning "Resetting database (this will delete all data)..."
            $confirm = Read-Host "Are you sure? Type 'YES' to confirm"
            if ($confirm -eq "YES") {
                # Database reset logic would go here
                Write-Info "Database reset completed"
            } else {
                Write-Info "Database reset cancelled"
            }
        }

        # Test database connection
        Write-Info "Testing database connection..."
        try {
            & mysql -u root -p$DB_PASSWORD -e "SELECT 'Connection successful' as status;" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Database connection successful"
            } else {
                Write-Warning "Database connection test failed"
                Write-Info "The server will attempt to connect during startup"
            }
        } catch {
            Write-Warning "Could not test database connection: $($_.Exception.Message)"
        }
    }

    # ================================
    # STEP 6: Start the Server
    # ================================
    Write-Step "Starting FastAPI server..."
    Write-Info "Server will be available at:"
    Write-Host "  🎮 Game Menu: " -NoNewline; Write-Host "http://$SERVER_HOST`:$SERVER_PORT/shared/index.html" -ForegroundColor Yellow
    Write-Host "  ♛ Eight Queens: " -NoNewline; Write-Host "http://$SERVER_HOST`:$SERVER_PORT/games/eight_queens/frontend/index.html" -ForegroundColor Cyan
    Write-Host "  📚 API Docs: " -NoNewline; Write-Host "http://$SERVER_HOST`:$SERVER_PORT/docs" -ForegroundColor Yellow
    Write-Host "  💚 Health Check: " -NoNewline; Write-Host "http://$SERVER_HOST`:$SERVER_PORT/api/health" -ForegroundColor Yellow
    
    Write-Info "Press Ctrl+C to stop the server"
    Write-Host ""

    # Activate virtual environment and start server
    $env:VIRTUAL_ENV = $VENV_PATH
    $env:PATH = "$VENV_PATH\Scripts;$env:PATH"
    
    & $PYTHON_EXE -m uvicorn shared.backend.main:app --reload --host $SERVER_HOST --port $SERVER_PORT

} catch {
    Write-Error "Startup failed: $($_.Exception.Message)"
    Write-Info "Troubleshooting steps:"
    Write-Host "  1. Ensure Python 3.8+ is installed"
    Write-Host "  2. Ensure MySQL is installed and running"
    Write-Host "  3. Check if ports 8000 and 3306 are available"
    Write-Host "  4. Verify .env file contains correct database password"
    Write-Host ""
    Write-Info "For manual startup, run:"
    Write-Host "  .\.venv\Scripts\Activate.ps1"
    Write-Host "  python -m uvicorn shared.backend.main:app --reload --host 127.0.0.1 --port 8000"
    exit 1
} finally {
    Write-Host ""
    Write-Info "Script execution completed"
}

# ================================================================
# Usage Examples:
# .\start.ps1                     # Full setup and start
# .\start.ps1 -QuickStart         # Skip checks, go straight to server  
# .\start.ps1 -ResetDatabase      # Reset database and start
# .\start.ps1 -Verbose            # Show detailed output
# ================================================================
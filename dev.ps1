Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# Verify Python version
$reqVersion = "3.12"
$pyVersion = (python --version).Split(" ")[1]
if ([version]$pyVersion -lt [version]$reqVersion) {
    Write-Error "Python $reqVersion+ required. Found: $pyVersion"
    exit 1
}

function Clean {
    Write-Host "Cleaning..." -ForegroundColor Green
    Remove-Item -Path "build","dist","__pycache__","*.pyc",".venv" -Recurse -Force -ErrorAction SilentlyContinue
}

function Setup {
    Write-Host "Setting up environment..." -ForegroundColor Green
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install -r requirements.txt
}

function Build {
    Write-Host "Building executable..." -ForegroundColor Green
    python build.py
}

function Run {
    Write-Host "Running game..." -ForegroundColor Green
    python main.py
}

function Test {
    Write-Host "Running tests..." -ForegroundColor Green
    pytest
}


$command = $args[0]
switch ($command) {
    "clean" { Clean }
    "setup" { Setup }
    "build" { Setup; Build }
    "run" { Setup; Run }
    "test" { Setup; Test }
    default {
        Write-Host @"
Usage: .\dev.ps1 <command>

Commands:
    clean       - Clean build artifacts and venv
    setup       - Create venv and install dependencies
    build       - Build executable
    run         - Run the game
    test        - Run tests
"@ -ForegroundColor Yellow
    }
}

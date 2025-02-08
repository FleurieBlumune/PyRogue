# PyRogue

## Requirements
- Python 3.12 or higher
- Windows with PowerShell

## First Time Setup
Run PowerShell as Administrator and execute:
```
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Development Commands
# Clean everything and start fresh
make clean

# Install dependencies
make deps

# Setup and activate virtual environment
make deps
source .venv/bin/activate

# Update requirements.txt with current deps
make verify-deps

# Build the executable
make build

# Run tests
make test

# Run the game
make run

# Do everything (install deps and build)
make all
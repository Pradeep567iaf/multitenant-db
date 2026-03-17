@echo off
REM Multi-Tenant System - Quick Start Script for Windows

echo ================================================
echo Multi-Tenant System - Quick Start
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/6] Checking Python installation... OK
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [2/6] Creating virtual environment...
    python -m venv venv
    echo Virtual environment created successfully!
    echo.
) else (
    echo [2/6] Virtual environment already exists... OK
    echo.
)

REM Activate virtual environment
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated!
echo.

REM Install dependencies
echo [4/6] Installing dependencies...
pip install -r requirements.txt
echo Dependencies installed successfully!
echo.

REM Initialize database
echo [5/6] Initializing database...
echo Make sure PostgreSQL is running and .env file is configured correctly.
echo.
python init_db.py
echo.

REM Ask user if they want to start services
echo ================================================
echo Setup Complete!
echo ================================================
echo.
echo Next steps:
echo 1. Make sure Redis is running: redis-server
echo 2. Start Celery worker in a new terminal:
echo    celery -A celery_worker worker --loglevel=info
echo 3. Start FastAPI server:
echo    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo API Documentation: http://localhost:8000/docs
echo Superadmin Login: admin@multitenant.com / admin123
echo.
echo For subdomain testing, add these entries to:
echo C:\Windows\System32\drivers\etc\hosts
echo   127.0.0.1    localhost
echo   127.0.0.1    abc.localhost
echo   127.0.0.1    xyz.localhost
echo.

pause

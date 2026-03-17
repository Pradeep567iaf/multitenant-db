@echo off
REM Multi-Tenant System - Run All Services Script

echo ================================================
echo Multi-Tenant System - Starting All Services
echo ================================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first or create venv manually.
    pause
    exit /b 1
)

echo [1/4] Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated!
echo.

echo [2/4] Checking Redis connection...
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo WARNING: Redis is not running. Starting Redis...
    start "Redis Server" redis-server
    timeout /t 3 /nobreak >nul
) else (
    echo Redis is running!
)
echo.

echo [3/4] Starting Celery Worker in new window...
start "Celery Worker" cmd /k "call venv\Scripts\activate.bat && celery -A celery_worker worker --loglevel=info"
echo Celery worker starting...
echo.

timeout /t 5 /nobreak >nul

echo [4/4] Starting FastAPI Server...
echo.
echo ================================================
echo Services Started Successfully!
echo ================================================
echo.
echo API Documentation: http://localhost:8000/docs
echo ReDoc: http://localhost:8000/redoc
echo Health Check: http://localhost:8000/health
echo.
echo Superadmin Login:
echo   Email: admin@multitenant.com
echo   Password: admin123
echo.
echo Tenant URLs (after creation):
echo   ABC Company: http://abc.localhost:8000
echo   XYZ Corp: http://xyz.localhost:8000
echo.
echo To stop:
echo   - Press Ctrl+C in this window to stop FastAPI
echo   - Close "Celery Worker" window to stop Celery
echo.
echo Testing Guide: TESTING_GUIDE.md
echo ================================================
echo.

REM Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

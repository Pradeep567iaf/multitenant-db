@echo off
REM Fix Celery Redis Issue

echo ================================================
echo Fixing Celery Redis Connection Issue
echo ================================================
echo.

if not exist "env" (
    echo ERROR: Virtual environment not found!
    echo Please run install_dependencies.bat first
    pause
    exit /b 1
)

echo [1/3] Activating virtual environment...
call env\Scripts\activate.bat
echo.

echo [2/3] Reinstalling Redis package...
pip uninstall -y redis
pip install redis==5.0.1
echo.

echo [3/3] Checking Redis server...
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo WARNING: Redis server is not running!
    echo.
    echo To start Redis server:
    echo   1. Open a NEW terminal window
    echo   2. Run: redis-server
    echo   3. Keep it running
    echo.
    echo OR if Redis is installed as Windows service:
    echo   Run: net start Redis
    echo.
) else (
    echo ✓ Redis server is running!
)
echo.

echo ================================================
echo Fix Complete!
echo ================================================
echo.
echo Next steps:
echo 1. Make sure Redis server is running (redis-server)
echo 2. Start Celery worker: celery -A celery_worker worker --loglevel=info
echo 3. Start FastAPI: uvicorn app.main:app --reload
echo.

pause

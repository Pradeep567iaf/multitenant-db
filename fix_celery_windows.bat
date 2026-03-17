@echo off
REM Complete Fix for Celery Redis Issue on Windows

echo ================================================
echo Fixing Celery Redis Issue on Windows
echo ================================================
echo.

if not exist "env" (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

echo [1/4] Activating virtual environment...
call env\Scripts\activate.bat
echo.

echo [2/4] Uninstalling old packages...
pip uninstall -y redis hiredis
echo.

echo [3/4] Installing compatible versions...
pip install redis==5.0.1
pip install hiredis==2.3.2
echo.

echo [4/4] Checking Redis server...
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Redis server is not running!
    echo.
    echo Please open a NEW terminal and run:
    echo   redis-server
    echo.
    echo Then keep that terminal open while running Celery.
    echo.
) else (
    echo.
    echo SUCCESS: Redis server is running!
    echo.
)

echo ================================================
echo Fix Applied!
echo ================================================
echo.
echo Next Steps:
echo 1. Make sure Redis server is running (redis-server)
echo 2. Start Celery worker:
echo    celery -A celery_worker worker --loglevel=info
echo.
echo 3. In another terminal, start FastAPI:
echo    uvicorn app.main:app --reload
echo.

pause

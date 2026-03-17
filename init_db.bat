@echo off
REM Initialize Database Script

echo ================================================
echo Initializing Multi-Tenant System Database
echo ================================================
echo.

if not exist "env" (
    echo ERROR: Virtual environment not found!
    echo Please run install_dependencies.bat first
    pause
    exit /b 1
)

echo [1/2] Activating virtual environment...
call env\Scripts\activate.bat
echo.

echo [2/2] Running database initialization...
echo.
python init_database.py
echo.

echo ================================================
echo Database Initialization Complete!
echo ================================================
echo.
echo Next steps:
echo 1. Run FastAPI server: run_server.bat
echo 2. Access http://localhost:8000/docs
echo 3. Create superadmin via POST /api/v1/auth/superadmin/create
echo.

pause

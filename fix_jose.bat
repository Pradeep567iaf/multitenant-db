@echo off
REM Fix jose package conflict

echo ================================================
echo Fixing python-jose Package
echo ================================================
echo.

if not exist "venv" (
    echo ERROR: Virtual environment not found!
    echo Please run install_dependencies.bat first
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo Uninstalling conflicting jose packages...
pip uninstall -y jose python-jose
echo.

echo Installing correct python-jose package...
pip install "python-jose[cryptography]==3.3.0"
echo.

echo ================================================
echo Fix Complete!
echo ================================================
echo.
echo You can now run: run_all.bat
echo.

pause

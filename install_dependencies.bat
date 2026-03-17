@echo off
REM Install all required dependencies

echo ================================================
echo Installing Multi-Tenant System Dependencies
echo ================================================
echo.

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created!
    echo.
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo Installing packages from requirements.txt...
pip install -r requirements.txt
echo.

echo ================================================
echo Installation Complete!
echo ================================================
echo.
echo You can now run: run_all.bat
echo.

pause

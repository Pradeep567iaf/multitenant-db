@echo off
REM Fix bcrypt/passlib compatibility issue

echo ================================================
echo Fixing bcrypt/passlib Compatibility
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

echo Upgrading bcrypt and passlib...
pip install --upgrade bcrypt
pip install --upgrade passlib[bcrypt]
echo.

echo Installing specific compatible versions...
pip install bcrypt==4.0.1
pip install passlib==1.7.4
echo.

echo ================================================
echo Fix Complete!
echo ================================================
echo.
echo Default credentials:
echo   Superadmin Email: admin@multitenant.com
echo   Superadmin Password: admin123
echo.
echo You can now run: run_all.bat
echo.

pause

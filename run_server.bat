@echo off
REM Start FastAPI Server with Uvicorn

echo ================================================
echo Starting Multi-Tenant System API Server
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

echo [2/2] Starting FastAPI server...
echo.
echo Access Swagger UI at: http://localhost:8000/docs
echo Access ReDoc at:        http://localhost:8000/redoc
echo API Base URL:           http://localhost:8000/api/v1
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

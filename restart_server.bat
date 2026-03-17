@echo off
REM Clear Python cache and restart server

echo ================================================
echo Clearing Python Cache
echo ================================================
echo.

echo Removing __pycache__ folders...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

echo Removing *.pyc files...
del /s /q *.pyc >nul 2>&1

echo.
echo Cache cleared!
echo.
echo Now starting FastAPI server...
echo.

call env\Scripts\activate.bat
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

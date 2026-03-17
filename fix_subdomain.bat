@echo off
REM Comprehensive Subdomain Fix Script

echo ================================================
echo Subdomain Login Fix - Complete Reset
echo ================================================
echo.

echo [1/4] Flushing DNS cache...
ipconfig /flushdns
echo.

echo [2/4] Checking database subdomains...
echo Please run this SQL query in your PostgreSQL:
echo.
echo SELECT id, name, email, subdomain FROM tenants;
echo.
echo Then verify subdomain is just 'abc' not full URL
echo.
pause

echo.
echo [3/4] Restarting FastAPI server...
echo Please stop the current FastAPI server (Ctrl+C) and restart it
echo.
pause

echo.
echo [4/4] Testing...
echo After restarting, try accessing: http://abc.localhost:8000/docs
echo.
echo If still not working, check:
echo 1. Browser cache - Use Incognito/Private mode
echo 2. Database subdomain value - Should be 'abc' only
echo 3. Hosts file - Verify it was saved correctly
echo.

pause

@echo off
REM Start Redis via WSL and launch Celery

echo ================================================
echo Starting Redis via WSL
echo ================================================
echo.

echo [1/3] Starting Redis in WSL...
wsl sudo service redis-server start
echo.

echo [2/3] Testing Redis connection...
python -c "import redis; r = redis.Redis(host='localhost', port=6379); print('✓ Redis is running!' if r.ping() else '✗ Redis not responding')"
echo.

echo [3/3] Ready to start Celery!
echo.
echo Next steps:
echo 1. Activate virtual environment: env\Scripts\activate.bat
echo 2. Start Celery: celery -A celery_worker worker --loglevel=info
echo.
echo Keep WSL terminal open for Redis to stay running!
echo.

pause

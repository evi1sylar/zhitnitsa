@echo off
echo ========================================
echo    Jitnica - Bakery Website
echo    Automatic startup script
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Install Python 3.10+
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Python check - OK
echo.

REM Create virtual environment
if not exist "venv\" (
    echo [2/5] Creating virtual environment...
    python -m venv venv
) else (
    echo [2/5] Virtual environment exists
)
echo.

REM Remove old database
if exist "db.sqlite3" (
    echo Removing old database...
    del /f db.sqlite3
    echo Database removed.
)
echo.

REM Activate virtual environment
echo [3/5] Installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.

REM Create migrations
echo [4/5] Creating database migrations...
python manage.py makemigrations
if %errorlevel% neq 0 (
    echo [ERROR] Migration creation failed!
    pause
    exit /b 1
)
echo.

REM Apply migrations
echo [4/5] Applying database migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo [ERROR] Migration apply failed!
    echo Check output above for details.
    pause
    exit /b 1
)
echo [4/5] Migrations applied successfully!
echo.

REM Create admin user
echo Creating admin user (if not exists)...
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@zhitnitsa.ru', 'admin123')" 2>nul
echo Admin created! (admin/admin123)
echo.

REM Create directories
if not exist "media\" mkdir media
if not exist "staticfiles\" mkdir staticfiles
echo Directories check - OK
echo.

REM Start server
echo [5/5] Starting server...
echo.
echo ========================================
echo    Site started!
echo    http://localhost:8000
echo    Opening browser in 3 seconds...
echo    Press Ctrl+C to stop
echo ========================================
echo.

timeout /t 3 /nobreak >nul
start http://localhost:8000

python manage.py runserver 8000

pause

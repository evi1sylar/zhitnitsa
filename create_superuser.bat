@echo off
chcp 65001 >nul
echo ========================================
echo    ^> Создание администратора ^<
echo ========================================
echo.

REM Активация виртуального окружения
if exist "venv\" (
    call venv\Scripts\activate.bat
)

echo Создайте суперпользователя для доступа к админке:
echo.
echo По умолчанию:
echo   Username: admin
echo   Password: admin123
echo.
echo Или введите свои данные:
echo.

python manage.py createsuperuser --noinput ^
    --username admin ^
    --email admin@zhitnitsa.ru 2>nul

if %errorlevel% neq 0 (
    echo.
    echo Если автоматическое создание не сработало, выполните:
    echo   python manage.py createsuperuser
    echo.
)

echo.
echo Администратор создан!
echo Вход в админку: http://localhost:8000/admin/
pause

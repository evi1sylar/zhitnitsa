@echo off
chcp 65001 >nul
echo ========================================
echo    ^> Житница - Сеть пекарен ^<
echo    Автоматический запуск сайта
echo ========================================
echo.

REM Проверка Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python не найден! Установите Python 3.10+
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Проверка Python - OK
echo.

REM Создание виртуального окружения
if not exist "venv\" (
    echo [2/5] Создание виртуального окружения...
    python -m venv venv
) else (
    echo [2/5] Виртуальное окружение уже существует
)
echo.

REM Активация виртуального окружения
echo [3/5] Установка зависимостей...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo.

REM Применение миграций
echo [4/5] Применение миграций базы данных...
python manage.py migrate --noinput
if %errorlevel% neq 0 (
    echo [WARNING] Миграции не выполнены, но запуск продолжится
)
echo.

REM Создание директорий для медиа и статики
if not exist "media\" mkdir media
if not exist "staticfiles\" mkdir staticfiles
echo [4/5] Проверка директорий - OK
echo.

REM Запуск сервера
echo [5/5] Запуск сервера...
echo.
echo ========================================
echo    Сайт запущен!
echo    http://localhost:8000
echo    Нажмите Ctrl+C для остановки
echo ========================================
echo.

python manage.py runserver 8000

pause

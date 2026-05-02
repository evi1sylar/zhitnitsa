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
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.

REM Применение миграций
echo [4/5] Создание миграций базы данных...
python manage.py makemigrations
if %errorlevel% neq 0 (
    echo [ERROR] Ошибка при создании миграций!
    pause
    exit /b 1
)
echo.

echo [4/5] Применение миграций базы данных...
python manage.py migrate
if %errorlevel% neq 0 (
    echo [ERROR] Ошибка при применении миграций!
    echo Проверьте вывод выше для деталей.
    pause
    exit /b 1
)
echo [4/5] Миграции применены успешно!
echo.

REM Создание суперпользователя если не существует
echo Проверка администратора...
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@zhitnitsa.ru', 'admin123')" 2>nul
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
echo    Открываю браузер...
echo    Нажмите Ctrl+C для остановки
echo ========================================
echo.

REM Открыть браузер через 3 секунды
timeout /t 3 /nobreak >nul
start http://localhost:8000

python manage.py runserver 8000

pause

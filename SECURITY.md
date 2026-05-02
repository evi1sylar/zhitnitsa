# Безопасность и оптимизация проекта "Житница"

## 📋 Выполненные улучшения

### 1. Оптимизация кода

#### Декоратор `@staff_required`
- **Проблема**: Дублирование проверки `if not request.user.is_staff` в каждом view
- **Решение**: Создан единый декоратор `bakery/decorators.py`
- **Экономия**: ~50 строк кода, централизованное управление доступом

#### N+1 проблема в `products` view
- **Проблема**: Итерация по всем продуктам для сбора тегов
- **Решение**: Использование `values_list()` для выборки данных
- **Улучшение**: Меньше запросов к БД, быстрее загрузка

#### Устранение дублирования
- Объединены функции `store_add` и `store_edit` → `store_add_edit`
- Единый декоратор для всех admin-only функций

### 2. Защита от уязвимостей

#### Валидация файлов (image upload)
- **Файл**: `bakery/utils.py`
- **Проверки**:
  - Разрешённые расширения: jpg, jpeg, png, gif, webp
  - Максимальный размер: 5MB
  - Обработка ошибок с пользовательскими сообщениями
- **Применение**: product_add, product_edit, store_add_edit

#### Защита от XSS
- **Django**: Автоматическое экранирование в шаблонах (`{{ variable }}`)
- **Мета-теги CSP**: Content-Security-Policy в base.html
- **Ограничение полей**: comment[:500], quantity (1-100)

#### CSRF защита
- Все POST формы используют `{% csrf_token %}`
- Django автоматически проверяет токен

#### Ограничение размера загрузки
- `DATA_UPLOAD_MAX_MEMORY_SIZE = 5MB`
- `FILE_UPLOAD_MAX_MEMORY_SIZE = 5MB`

#### Защита от Clickjacking
- `X-Frame-Options: SAMEORIGIN` (meta + settings)

#### Защита от MIME sniffing
- `X-Content-Type-Options: nosniff`

### 3. Аутентификация и авторизация

- **@login_required**: Для всех функций, требующих входа
- **@staff_required**: Для админских функций
- **Проверка прав**: order_cancel (только свои заказы)
- **Защита от самов удаления**: user_delete проверяет `user_to_delete.pk == request.user.pk`

### 4. Безопасность паролей

- Django автоматически хеширует пароли (PBKDF2)
- Токенная система сброса пароля
- Валидация сложности (минимум 8 символов, проверка совпадения)

### 5. SQL Injection защита

- Используется ORM Django (защита по умолчанию)
- `get_object_or_404()` вместо сырых SQL запросов
- Параметризованные фильтры

## 🔒 Рекомендации для production

### 1. SECURITY SETTINGS (zhitnitsa/settings.py)
```python
# Включить в production:
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 год
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### 2. SECRET_KEY
```python
# Использовать переменную окружения
import os
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
```

### 3. DATABASE
```python
# Использовать PostgreSQL вместо SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'zhitnitsa',
        'USER': 'postgres',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 4. EMAIL для сброса пароля
```python
# Настроить реальную отправку email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yourprovider.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASS')
```

### 5. LOGGING
```python
# Настроить логирование ошибок
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'logs/errors.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

### 6. RATE LIMITING
Установите django-ratelimit для защиты от брутфорса:
```python
# pip install django-ratelimit
# В urls.py:
from ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m')
def login_view(request):
    # ...
```

### 7. CORS (если есть API)
```python
# pip install django-cors-headers
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
]
```

## 📊 Оптимизация производительности

### 1. Кэширование
```python
# pip install django-redis
# В settings.py:
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# В views.py:
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # 15 минут
def products(request):
    # ...
```

### 2. Базза данных
- Индексы на часто используемые поля (tags, status, created_at)
- Пагинация для больших списков

### 3. Статика
```python
# В production использовать WhiteNoise или CDN
INSTALLED_APPS += ['whitenoise.runserver_nostatic']
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
```

## 🧪 Тестирование безопасности

### Проверки перед деплоем:
1. [ ] DEBUG = False
2. [ ] SECRET_KEY не в коде
3. [ ] HTTPS перенаправление включено
4. [ ] CSRF защита работает
5. [ ] Файлы валидируются
6. [ ] Права доступа проверены
7. [ ] SQL injection защита (ORM)
8. [ ] XSS защита (автоматическая в Django)
9. [ ] Логирование ошибок
10. [ ] Резервное копирование БД

### Инструменты для проверки:
```bash
# Django security check
python manage.py check --deploy

# Поиск уязвимостей в зависимостях
pip install safety
safety check

# Проверка кода
pip install bandit
bandit -r bakery/
```

## 📝 Чеклист для новых функций

При добавлении новой функциональности проверьте:
- [ ] Нужна ли авторизация?
- [ ] Нужна ли проверка staff?
- [ ] Есть ли CSRF токен в форме?
- [ ] Валидируется ли ввод пользователя?
- [ ] Ограничен ли размер файлов?
- [ ] Экранируется ли вывод в шаблонах?
- [ ] Обработаны ли исключения?
- [ ] Есть ли логирование?

---
**Последнее обновление**: 2026-05-02
**Версия проекта**: 1.0

import os
from django.core.exceptions import ValidationError


ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp']
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_image_file(file_obj):
    """
    Проверяет файл изображения на:
    - Расширение
    - Размер
    - Возвращает ошибку или None
    """
    if not file_obj:
        return None
    
    # Проверка расширения
    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext.lstrip('.') not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(f'Разрешены только изображения: {", ".join(ALLOWED_IMAGE_EXTENSIONS)}')
    
    # Проверка размера
    if hasattr(file_obj, 'size') and file_obj.size > MAX_IMAGE_SIZE:
        raise ValidationError(f'Размер изображения не должен превышать 5MB')
    
    return None

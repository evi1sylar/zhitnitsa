from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test


def staff_required(view_func):
    """Декоратор для проверки доступа только администраторам."""
    return user_passes_test(lambda u: u.is_staff, login_url='home')(view_func)

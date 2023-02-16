from datetime import datetime
from typing import Dict

from django.http import HttpRequest


def year(request: HttpRequest) -> Dict[str, int]:
    """Добавляет переменную с текущим годом.

    Args:
        request (HttpRequest): объект, содержащий HTTP-запрос от клиента.

    Returns:
        Словарь с одной парой ключ-значение:
        'year' (str): текущий год в целочисленном представлении.
    """
    del request
    return {
        'year': datetime.now().year,
    }

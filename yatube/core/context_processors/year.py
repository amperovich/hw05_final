from datetime import datetime
from typing import Dict

from django.http import HttpRequest


def year(request: HttpRequest) -> Dict[str, int]:
    """Добавляет переменную с текущим годом."""
    del request
    return {
        'year': datetime.now().year,
    }

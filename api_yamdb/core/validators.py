import re

from django.core.exceptions import ValidationError
from django.utils import timezone

from api_yamdb.settings import INCORRECT_USERNAMES


def validate_year(value):
    """Валидатор для проверки корректного года."""
    if value > timezone.now().year:
        raise ValidationError(
            message=f'{value} еще не наступил.',
        )


def validate_username(incoming_username):
    """Валидатор проверяет полученный username
    на соответствие списку запрещенных имен и символов."""
    for username in INCORRECT_USERNAMES:
        if re.match(username, incoming_username):
            raise ValidationError(f'Имя "{incoming_username}" запрещено.')
    return incoming_username

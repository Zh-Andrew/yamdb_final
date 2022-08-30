from django.utils import timezone

from django.core.exceptions import ValidationError


def username_validation(value):
    if value.lower() == 'me':
        raise ValidationError(
            'Username <me> is prohibited',
            params={'value': value}
        )
    return value


def year_validation(value):
    if value > timezone.now().year:
        raise ValidationError(
            f'{value} - неверное значение'
        )

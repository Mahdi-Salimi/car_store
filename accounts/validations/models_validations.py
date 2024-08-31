import re

from django.core.exceptions import ValidationError

def validate_phone_number(value):
    pattern = r'^09\d{9}$'
    if not re.match(pattern, value):
        raise ValidationError(
            'Phone number must be in the format: 09 followed by exactly 9 digits.',
            params={'value': value},
        )
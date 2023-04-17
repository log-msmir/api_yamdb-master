from django.core.exceptions import ValidationError


def role_validator(role):
    if role not in ['user', 'moderator', 'admin']:
        raise ValidationError(message='The role must be one of: user, moderator or admin')

def ascii_validator(string):
    errors = [ord(char) for char in string if ord(char) > 127]
    if errors:
        raise ValidationError(message='Slug must be in ASCII characters')
        